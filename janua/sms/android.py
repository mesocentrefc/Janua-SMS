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

import datetime
import errno
import json
import socket
import time

from janua.utils.android.adb import AdbError, AdbProtocolError, AdbShellError
from janua.utils.android.android import Android, AndroidRpcError
from janua.sms.engine import SMSEngine
from janua.sms import SMSError, ModemError

config_spec = """
#
# android section
#
[android]
message_timeout = integer(1000, 30000, default=1000)    ; process message timeout in ms for each message received, for slower devices grow this value
"""

class AndroidSMS(SMSEngine):
    """Android SMS class interface"""
    name = 'android'
    config_spec = config_spec

    action = 'android.provider.Telephony.SMS_RECEIVED'

    def __init__(self, config):
        """
        Initialize stuff

        :param config: config object parameter
        """
        self._timeout_message = config.android.message_timeout
        local_event_port = 12345

        try:
            self.droid = Android(config)
            self.droid.eventRegisterForBroadcast(self.action, False)
            port = self.droid.startEventDispatcher()
        except (AdbError, AdbProtocolError, AndroidRpcError), msg:
            raise SMSError(msg)

        connected = False
        for i in xrange(0, 10):
            try:
                self.droid.client.forward('tcp:%d' % (local_event_port), 'tcp:%d' % port['result'])
            except (AdbError, AdbProtocolError, AdbShellError), msg:
                local_event_port += 1
                continue
            else:
                connected = True
                break                

        if not connected:
            raise SMSError('Event connection with android phone failed')

        try:
            self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sk.connect(('localhost', local_event_port))
            self.sk.settimeout(None)
            self.skevent = self.sk.makefile()
        except socket.error:
            emsg = 'Error while connecting to localhost on port %d' % local_event_port
            raise SMSError(emsg)

    def send(self, message, to):
        """
        Send SMS from an android device

        :param message: message to send
        :param to: a phone number or all string to send to all contact numbers
        :returns: a tuple with reference which identify message and number of
                  slices of SMS sent (multi-part) or tuple of None if not supported
        """
        try:
            self.droid.smsSend(to, message)
            return (None, None)
        except AndroidRpcError, msg:
            raise SMSError('Failed to send SMS to %s: %s' % (to, msg))

    def event(self):
        """
        Listen on SMS received event

        :returns: True when an SMS is received from device, otherwise False
                  or raise an exception when an error occur
        """
        event_received = False

        try:
            event_data = self.skevent.readline()
        except socket.error, (code, msg):
            raise ModemError('Failed to read event on socket: %s (%s)' % (msg, errno.errorcode[code]))
        else:
            try:
                d = json.loads(event_data)
                data = json.loads(d['data'])
                if data['action'] == self.action:
                    return True
            except ValueError:
                raise ModemError('Failed to decode json event data: %s' % event_data)
            except KeyError:
                pass

        return event_received

    def process(self):
        """
        Get unread inbox message

        :returns: a list of messages
        """
        messages = []

        time.sleep(self._timeout_message/1000)

        try:
            msg = self.droid.smsGetMessages(True)
        except AndroidRpcError, err:
            raise SMSError('Failed to get messages on device: %s' % err)
        else:
            if msg['result']:
                for m in msg['result']:
                    body = m['body']
                    address = m['address']
                    mdate = int(m['date'][:-3])
                    d = datetime.datetime.fromtimestamp(mdate)

                    messages.append({
                        'body': body,
                        'address': address,
                        'date': d,
                        'status': None,
                    })
                    try:
                        self.droid.smsDeleteMessage(int(m['_id']))
                    except AndroidRpcError, msg:
                        raise SMSError('Failed to delete messages on device: %s' % msg)

        return messages

    def stop(self):
        """
        Stop event dispatcher and SL4A server, raise an exception when an error occur
        """
        # close the socket on device side to force blocking read to quit
        try:
            self.droid.stopEventDispatcher()
            self.droid.eventUnregisterForBroadcast(self.action)
        except AndroidRpcError, msg:
            raise ModemError('Failed to stop event dispatcher: %s' % msg)
        else:
            self.sk.close()
        finally:
            try:
                self.droid.stop()
            except AndroidRpcError, msg:
                raise ModemError('Failed to stop SL4A server: %s' % msg)
