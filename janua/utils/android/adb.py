# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# Copyright (c) 2016 Cédric Clerget - HPC Center of Franche-Comté University
#
# This file is part of Janua-SMS
#
# http://github.com/mesocentrefc/Janua-SMS
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import socket
import stat
import struct
import subprocess
import zipfile

import janua.utils.logger as jlogger

from janua.utils.android import PLATFORM_TOOLS_PATH
from janua.utils.android import ADB_PATH, ADB_PORT, LOCALHOST

log = jlogger.getLogger(__name__)

# Taken from file_sync_service.h for file transfer support
ID = lambda x: (ord(x[0]) | (ord(x[1]) << 8) | (ord(x[2]) << 16) | (ord(x[3]) << 24))

# Sync requests id
ID_OKAY = ID('OKAY')
ID_FAIL = ID('FAIL')
ID_QUIT = ID('QUIT')
ID_DONE = ID('DONE')
ID_DATA = ID('DATA')
ID_SEND = ID('SEND')
ID_RECV = ID('RECV')
ID_STAT = ID('STAT')
ID_LIST = ID('LIST')
ID_ULNK = ID('ULNK')
ID_DENT = ID('DENT')

# sync data maximum chunk size
SYNC_CHUNK_MAX = (64 * 1024)

class AdbError(Exception):
    """
    ADB general error exception
    """
    pass

class AdbShellError(Exception):
    """
    ADB shell error exception, raised when a shell command failed to execute on device
    """
    pass

class AdbProtocolError(Exception):
    """
    ADB protocol related error
    """
    pass

def _FoundAdbBinary():
    for path in os.environ['PATH'].split(os.pathsep):
        filepath = os.path.join(path, 'adb')
        if os.access(filepath, os.X_OK):
            return True
    return False

def _InstallAdb(destination, config):
    """
    Install adb binary if not installed on system
    """
    if not _FoundAdbBinary():
        log.debug('Installing ADB binary, path %s' % destination)
        try:
            zf = zipfile.ZipFile(PLATFORM_TOOLS_PATH)
        except Exception, err:
            log.error('Can not open zip file %s: %s' % (path, err))
        else:
            for name in zf.namelist():
                if 'adb' in name:
                    path = os.path.dirname(destination)
                    if not os.path.exists(path):
                        os.mkdir(path)
                    try:
                        f = open(destination,'wb')
                        f.write(zf.read(name))
                        os.chmod(destination, stat.S_IRWXU |
                                              stat.S_IRGRP |
                                              stat.S_IXGRP |
                                              stat.S_IROTH |
                                              stat.S_IXOTH)
                    except Exception, err:
                        log.error('Can not write adb binary into %s: %s' % (destination, err))
                    else:
                        f.close()
            zf.close()

def _AdbCommand(command):
    pipe = subprocess.PIPE
    try:
        return subprocess.call(['adb', '-P', str(ADB_PORT), command], stderr=pipe, stdout=pipe)
    except Exception, err:
        log.error('Failed to execute adb command: %s' % err)

def _StopAdbServer():
    """
    Stop adb server
    """
    return _AdbCommand('kill-server')

def _StartAdbServer(config):
    """
    Start adb server
    """
    _InstallAdb(ADB_PATH, config)
    return _AdbCommand('start-server')


class AdbSmartSocketClient(object):
    """
    Python client using ADB smart sockets
    """
    def __init__(self, config):
        self.client = None
        self.htype = 'host'
        self.ttype = 'transport-any'
        self.config = config
        self._connect()
        self.waitForDevice()

    def _connect(self):
        """
        Connect to ADB smart socket

        :returns: socket connection
        """
        log.debug('Starting ADB socket connection')
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        retry = 1
        while retry < 3:
            try:
                conn = self.client.connect((LOCALHOST, ADB_PORT))
            except socket.error:
                log.warning('Couldn\'t connect to %s on port %s' % (LOCALHOST, ADB_PORT))
                log.info('Trying to start ADB server [Try %d]' % retry)
                if _StartAdbServer(self.config) != 0:
                    log.error('ADB server didn\'t start')
                retry += 1
            else:
                return conn
        raise AdbError('Connection to ADB server failed')

    def _close(self):
        """
        Close ADB smart socket connection
        """
        log.debug('Closing ADB socket connection')
        self.client.close()

    def _request(self, req):
        """
        Send request using the following format:
          * A 4-byte hexadecimal string giving the length of the payload
          * Followed by the payload itself.

        :param req: service request
        :returns: the number of bytes written
        """
        return self._write('%04x%s' % (len(req), req))

    def _setTransport(self):
        """
        Set transport type

        :returns: nothing or raise an exception if an error occured
        """
        self._connect()
        s = '%s:%s' % (self.htype, self.ttype)
        log.debug('Setting transport: %s' % s)
        self._request(s)
        try:
            self._status()
        except AdbError:
            log.error('local service transport request %s failed' % s)
            self._close()
            raise

    def _hostService(self, service):
        """
        Host service request

        :param service: service to request
        :returns: the request status in case of a forward service, otherwise return the
                  server response or raise an exception when service request failed
        """
        self._connect()
        s = '%s:%s' % (self.htype, service)
        log.debug('Sending host service request: %s' % s)
        self._request(s)
        try:
            self._status()
            if 'forward' in service:
                response = self._status()
            elif 'track-devices' in service:
                while True:
                    response = self._response()
                    if 'device' in response:
                        break
            else:
                response = self._response()
        except AdbProtocolError, AdbError:
            log.error('host service request %s failed' % s)
            self._close()
            raise
        self._close()
        return response

    def _localService(self, service):
        """
        Local service request, set the transport type before sending service request

        :param service: service to request
        :returns: the server response or raise an exception when service request failed
        """
        self._setTransport()
        log.debug('Sending local service request: %s' % service)
        self._request(service)
        try:
            self._status()
            response = self._chunkResponse()
        except AdbProtocolError, AdbError:
            log.error('local service request %s failed' % service)
            self._close()
            raise
        self._close()
        return response

    def _syncStart(self):
        """
        Start sync mode
        """
        self._setTransport()
        log.debug('Sending sync mode request')
        self._request('sync:')
        try:
            self._status()
        except AdbError:
            log.error('sync service failed')
            self._close()
            raise

    def _syncSend(self, localfile, remfile):
        """
        Send binary data during sync mode

        :returns: nothing or raise an AdbError exception if file transfer failed
        """
        try:
            f = open(localfile)
        except IOError:
            error = 'Error while opening %s' % localfile
            log.error(error)
            raise AdbError(error)

        st = os.stat(localfile)
        mode = st.st_mode
        mtime = st.st_mtime
        fname = '%s,%d' % (remfile, mode)
        fname.encode('utf-8')
        log.debug('Sending sync request id ID_SEND: %s', fname)
        self._write(struct.pack('II', ID_SEND, len(fname)))
        self._write(fname)
        try:
            data = f.read(SYNC_CHUNK_MAX)
            while data:
                log.debug('Sending sync request id ID_DATA, data length: %d' % len(data))
                self._write(struct.pack('II', ID_DATA, len(data)))
                self._write(data)
                data = f.read(SYNC_CHUNK_MAX)
        except:
            log.error('Error while transferring file %s' % localfile)
            self._close()
            raise AdbError('File transfer failed')
        finally:
            f.close()
        log.debug('Sending sync request id ID_DONE, mtime: %d', mtime)
        self._write(struct.pack('II', ID_DONE, mtime))
        status, msglen = struct.unpack('II', self._read(struct.calcsize('II')))
        if status == ID_FAIL:
            msg = self._read(msglen)
            log.error('File transfer failed: %s' % msg)
            raise AdbError('File transfer failed: %s' % msg)
        elif status == ID_OKAY:
            log.info('File transfer success')
        else:
            raise AdbError('File transfer unknown status')

    def _syncQuit(self):
        """
        Sync mode quit
        """
        log.debug('Sending sync request id ID_QUIT')
        self._write(struct.pack('II', ID_QUIT, 0))
        self._close()

    def _read(self, size):
        """
        Read data size on server socket

        :param size: size of data to read
        :returns data read
        """
        return self.client.recv(size)

    def _write(self, data):
        """
        Write data to server socket

        :param data: data to write
        :returns length of data written
        """
        return self.client.send(data)

    def _response(self):
        """
        Read server response

        :returns response message or raise an exception if an error occured
        """
        size = self._read(4)
        try:
            sz = int(size, 16)
        except ValueError:
            log.error('Error while getting message size, size returned %s' % size)
            raise AdbProtocolError('Wrong size')
        return self._read(sz)

    def _chunkResponse(self, chunk_size=4096):
        """
        Read server response by chunk of size chunk_size

        :param chunk_size: size of chunk to read
        :returns: data response
        """
        data = self._read(chunk_size)
        response = data
        while data:
            data = self._read(chunk_size)
            response += data
        return response

    def _status(self):
        """
        Read request status

        :returns: OKAY string or raise an exception if status failed
        """
        status = self._read(4)
        if status == 'OKAY':
            return status
        elif status == 'FAIL':
            error_message = self._response()
            log.error(error_message)
            raise AdbError(error_message)

    def stop(self):
        """
        Stop ADB server
        """
        log.debug('Stopping ADB server')
        if _StopAdbServer() != 0:
            log.error('ADB server didn\'t stop')

    def version(self):
        """
        Get ADB version

        :returns: a version integer
        """
        log.debug('Getting ADB version')
        try:
            version = int(self._hostService('version'), 16)
        except:
            raise AdbProtocolError('Wrong ADB version')
        return version

    def shell(self, cmdline, status_only=True):
        """
        Execute a shell command on device

        :param cmdline: command line to execute
        :param status_only: if set to True, function return the exit status, no command output
                            if set to False, function return command output, no exit status
        :returns: a string 'OK' or raise an exception if an error occured when status_only set to True.
                command output when status_only set to False.
        """
        log.debug('Executing %s on device' % cmdline)

        if not status_only:
            return self._localService('shell:%s' % cmdline)

        cmd = 'shell:%s > /dev/null 2>&1; if [ $? != 0 ]; then echo "KO"; else echo "OK"; fi' % cmdline
        output = self._localService(cmd)

        if 'KO' in output:
            raise AdbShellError('The following command line failed on device: %s' % cmdline)

        return output

    def forward(self, local, remote):
        """
        Forward local connections from local to remote address

        :param local: local address (example format: tcp:<port>, local:<path>, dev:<path>)
        :param remote: remote address
        """
        log.debug('Setting forward connection from %s to %s' % (local, remote))
        return self._hostService('forward:%s;%s' % (local, remote))

    def killForwardAll(self):
        """
        Kill all forward connections
        """
        log.debug('Killing all forward connections')
        return self._hostService('killforward-all')

    def listForward(self):
        """
        List all existing forward connections

        :returns: existing forward connections
        """
        log.debug('Listing all existing forward connections')
        return self._hostService('list-forward')

    def getState(self):
        """
        Get state of device

        :returns: the state of a given device as a string
        """
        log.debug('Getting state of device')
        return self._hostService('get-state')

    def getSerialNo(self):
        """
        Get serial number of device
        :returns: the serial number of the device
        """
        log.debug('Getting serial number of device')
        return self._hostService('get-serialno')

    def push(self, localfile, remotefile):
        """
        Push a local file on device. Don't support directory

        :param localfile: file path on host
        :param remotefile: file path destination on device
        :returns: nothing or raise an exception if an error occured
        """
        log.debug('Pushing local file %s to %s on device' % (localfile, remotefile))
        self._syncStart()
        try:
            self._syncSend(localfile, remotefile)
        except AdbError:
            raise
        finally:
            self._syncQuit()

    def waitForDevice(self):
        """
        Wait for device, don't return until a device is detected

        :returns: string representing a list of device
        """
        log.debug('Waiting for device ...')
        return self._hostService('track-devices')

    def reboot(self):
        """
        Reboot the device
        """
        log.debug('Rebooting device ...')
        return self._localService('reboot:boot')
