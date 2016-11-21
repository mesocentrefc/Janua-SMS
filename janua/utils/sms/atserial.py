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

import serial
import threading

try:
    bytes
    bytearray
except (NameError, AttributeError):
    from serial import bytearray, bytes

import janua.utils.logger as jlogger

log = jlogger.getLogger(__name__)

_finalResponsesError = [
    'ERROR', '+CMS ERROR:', '+CME ERROR:',
    'NO CARRIER', 'NO ANSWER', 'NO DIALTONE'
]
_finalResponsesSuccess = ['OK', 'CONNECT']
_smsUnsoliciteds = ['+CMT:', '+CDS:', '+CBM:']
_otherUnsoliciteds = [
    '%CTZV:', '+CRING:', 'RING', 'NO CARRIER',
    '+CCWA', '+CREG:', '+CGREG:', '+CGEV:'
]

SerialException = serial.serialutil.SerialException

BYTESIZE = {'5': serial.FIVEBITS, '6': serial.SIXBITS,
            '7': serial.SEVENBITS, '8': serial.EIGHTBITS}

PARITY = {'none': serial.PARITY_NONE, 'even': serial.PARITY_EVEN,
          'odd': serial.PARITY_ODD, 'mark': serial.PARITY_MARK,
          'space': serial.PARITY_SPACE}

STOPBITS = {'1': serial.STOPBITS_ONE, '1.5': serial.STOPBITS_ONE_POINT_FIVE,
            '2': serial.STOPBITS_TWO}

def isFinalResponseError(line):
    """
    Is there a response error line
    """
    for resp in _finalResponsesError:
        if line.startswith(resp):
            return True
    return False

def isFinalResponseSuccess(line):
    """
    Is there a response success line
    """
    for resp in _finalResponsesSuccess:
        if line.startswith(resp):
            return True
    return False

def isSMSUnsolicited(line):
    """
    Is there an unsolicited sms response line 
    """
    for u in _smsUnsoliciteds:
        if line.startswith(u):
            return True
    return False

def isUnsolicited(line):
    """
    Is there an unsolicited response line
    """
    for u in _otherUnsoliciteds:
        if line.startswith(u):
            return True
    return False

class ATSerial(serial.Serial):
    """
    An object Serial class to send AT command on serial port 
    """
    def __init__(self, *args, **kw):
        super(ATSerial, self).__init__(*args, **kw)
        self.command = True
        self.response_err = None
        self.finalresponses = []
        self.commandmutex = threading.Lock()
        self.commandcond = threading.Condition(self.commandmutex)
        self.smsMsg = None

    def clear_command(self):
        """
        Clear command response and error 
        """
        self.command = False
        self.response_err = None
        self.finalresponses = []
        self.smsMsg = None

    def readline(self, size=None, eol='\r\n'):
        """
        Read a line which is terminated with end-of-line (eol) character ('\n' by default) or until timeout.

        :param size: number of character to read before returning
        :param eol: end of line sequence
        :returns: bytes read
        """
        leneol = len(eol)
        line = bytearray()
        while True:
            c = self.read(1)
            if c:
                line += c
                if line[0:2] == '> ':
                    break
                if line[-leneol:] == eol:
                    return bytes(line[:-leneol])
                if size is not None and len(line) >= size:
                    break
            else:
                break
        return bytes(line)

    def write(self, data):
        """
        Write data on serial port ended with carriage return

        :param data: data to send
        :returns: number of bytes written.
        """
        log.debug('Sending AT command: %s' % data)
        return super(ATSerial, self).write('%s\r' % data)

    def at_init_command(self, command, lines=3):
        """
        Send AT init command to initialize modem

        :param command: AT command to send without AT prefix
        :param lines: maximum number of lines to read
        :returns: a tuple (err, resp) where err is a boolean indicating if at command return an error or not
                  and resp is a list containing lines returned by AT command
        """
        self.write('AT%s\r' % command)

        while lines >= 0:
            line = self.readline()
            lines -= 1
            if line != '':
                self.processline(line)
                err = self.response_err
                resp = self.finalresponses
                if err != None:
                    self.clear_command()
                    return err, resp

        self.clear_command()
        log.debug('Command not responding')
        return self.response_err, self.finalresponses

    def at_command(self, command):
        """
        Send AT command

        :param command: AT command to send without AT prefix
        :returns: a tuple (err, resp) where err is a boolean indicating if at command return an error or not
                  and resp is a list containing lines returned by AT command
        """
        self.commandcond.acquire()
        
        self.write('AT%s\r' % command)

        self.commandcond.wait()

        err = self.response_err
        resp = self.finalresponses

        self.clear_command()

        self.commandcond.release()
        
        return err, resp
    
    def at_command_sms(self, msg, msglen):
        """
        Send AT sms command with content

        :param msg: pdu content
        :param msglen: pdu content length
        :returns: a at_command tupple
        """
        self.smsMsg = msg
        return self.at_command('+CMGS=%d' % msglen)
    
    def processline(self, line):
        """
        Process a line read from serial port

        :param line: line to be processed
        """
        self.commandcond.acquire()

        if isFinalResponseSuccess(line):
            self.response_err = False
            self.finalresponses.append(line)
            self.commandcond.notifyAll()
        elif isFinalResponseError(line):
            self.response_err = True
            self.finalresponses.append(line)
            self.commandcond.notifyAll()
        elif self.smsMsg != None and line == '> ':
            self.write_ctrl_z(self.smsMsg)
        elif not isUnsolicited(line):
            self.finalresponses.append(line)

        self.commandcond.release()
    
    def write_ctrl_z(self, data=''):
        """
        Write data on serial port ended with CTRL-Z

        :param data: data to send
        :returns: number of bytes written.
        """
        return super(ATSerial, self).write('%s\x1a' % data)
