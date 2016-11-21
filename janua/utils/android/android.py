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

import errno
import json
import socket
import time

import janua.utils.logger as jlogger

from janua.utils.android.adb import AdbSmartSocketClient, AdbError
from janua.utils.android.adb import AdbProtocolError, AdbShellError
from janua.utils.android import LOCALHOST, SL4A_HOST_PORT
from janua.utils.android import SL4A_SERVER_PORT, SL4A_PATH

log = jlogger.getLogger(__name__)

class AndroidRpcError(Exception):
    pass

class Android(object):
    """
    Android RPC client to communicate with SL4A server
    """
    id = 0

    def __init__(self, config, addr=(LOCALHOST, SL4A_HOST_PORT)):
        """
        Initialize connection to SL4A server

        :param addr: a tuple containing hostname (default: localhost) and port (default: 9999)
        """

        self.client = AdbSmartSocketClient(config)
        output = self.client.shell('pm path com.googlecode.android_scripting', False)

        # Install SL4A apk on smartphone if not already installed
        if 'package' not in output:
            log.debug('SL4A package not found on device, downloading and installing SL4A package')
            lpath = SL4A_PATH
            filename = lpath.split('/')[-1]
            rpath = '/data/local/tmp/%s' % filename
            self.client.push(lpath, rpath)
            try:
                self.client.shell('pm install %s' % rpath)
            except AdbShellError:
                log.error('Unable to install package %s' % filename)
            finally:
                self.client.shell('rm %s' % rpath)

        log.debug('Initialize connection to %s on port %s', addr[0], addr[1])
        retry = 1
        while retry < 3:
            try:
                self._connection = socket.create_connection(addr)
            except socket.error:
                try:
                    self.start()
                except (AdbError, AdbProtocolError, AdbShellError), msg:
                    raise AndroidRpcError(msg)
                retry += 1
            else:
                self._file = self._connection.makefile()
                break

    def start(self):
        """
        Start SL4A private server
        """
        log.debug('Start SL4A private server')
        self.client.killForwardAll()
        self.client.shell('am start -a com.googlecode.android_scripting.action.KILL_ALL ' +
                           '-n com.googlecode.android_scripting/.activity.ScriptingLayerServiceLauncher')
        self.client.shell('am start -a com.googlecode.android_scripting.action.LAUNCH_SERVER ' +
                           '-n com.googlecode.android_scripting/.activity.ScriptingLayerServiceLauncher ' +
                           '--ei com.googlecode.android_scripting.extra.USE_SERVICE_PORT %d' % SL4A_SERVER_PORT)
        self.client.forward('tcp:%d' % SL4A_HOST_PORT, 'tcp:%d' % SL4A_SERVER_PORT)
        # wait a bit for slower devices
        time.sleep(1)

    def _rpc(self, method, *args):
        """
        Call API methods supported by SL4A

        :param method: API method to call with args
        :returns: a dictionary with following fields: error, result, id
        """
        log.debug('Calling method %s with args: %s', method, repr(args))

        data = {'id': self.id, 'method': method, 'params': args}
        try:
            request = json.dumps(data)
        except ValueError:
            raise AndroidRpcError('Error while encoding json request')

        try:
            self._file.write('%s\n' % request)
            self._file.flush()

            response = self._file.readline()
        except socket.error, (code, msg):
            raise AndroidRpcError('Error while calling API method %s: %s (%s)' % (method, msg, errno.errorcode[code]))

        try:
            result = json.loads(response)
        except ValueError:
            raise AndroidRpcError('Error while decoding json response')

        self.id += 1

        if result['error'] is not None:
            raise AndroidRpcError(result['error'])

        return result

    def __getattr__(self, name):
        """
        SL4A API wrapper

        :param name: API name method to call
        """
        def rpc_call(*args):
            return self._rpc(name, *args)
        return rpc_call

    def stop(self):
        """
        Stop SL4A server and kill all forward connections
        """
        log.debug('Stop SL4A private server')
        try:
            self.client.shell('am start -a com.googlecode.android_scripting.action.KILL_ALL ' +
                               '-n com.googlecode.android_scripting/.activity.ScriptingLayerServiceLauncher')
            self.client.killForwardAll()
        except (AdbError, AdbProtocolError, AdbShellError), msg:
            raise AndroidRpcError(msg)
        finally:
            self.client.stop()

        self._connection.close()
