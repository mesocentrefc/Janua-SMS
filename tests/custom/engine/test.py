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
import time
import Queue

from janua.sms.engine import SMSEngine

class TestSMS(SMSEngine):
    """
    Abstract class for SMS interface
    """

    name = 'test'

    """Engine name"""

    config_spec = ""
    """
    Configuration specification for this engine. You can refer to `configobj documentation <http://www.voidspace.org.uk/python/configobj.html#configspec>`_
    """

    def __init__(self, config):
        """
        Engine initialization

        :param config: global configuration object
        """
        self.send_queue = Queue.Queue()
        self.recv_queue = Queue.Queue()
        pass

    def reconnect(self, event):
        """
        Try to connect to modem or service in case of communication error
        with modem

        :param event: a threading event object
        """
        while not event.isSet():
            time.sleep(1)

    def send(self, message, to):
        """
        Send SMS

        :param message: a text message to send
        :param to: recipient phone number
        :returns: a tuple containing reference which identify message and number of parts
                  in case of multi-part SMS. Replace by None values if you don't need to
                  support multi-part SMS or if your engine use a service which take care
                  of multi-part message
        """
        self.send_queue.put((message, to))
        return (None, None)

    def get_send_messages(self):
        message = []
        timeout = 1
        while(1):
            try:
                message.append(self.send_queue.get(True, 1))
            except Queue.Empty:
                if timeout == 0:
                    break
                timeout -= 1
                continue
            if self.send_queue.empty():
                break
        return message

    def fake_receive(self, message, sender):
        msg = {
            'body': message,
            'address': sender,
            'date': datetime.datetime.now(),
            'status': None
        }
        self.recv_queue.put(msg)

    def event(self):
        """
        Listen event

        :returns: True when a message is received or False when there is no message
        """
        return not self.recv_queue.empty()

    def process(self):
        """
        Process SMS

        :returns: a list of messages as dictionary
        
        Message dictionary must contain followings keys:

          * **body:** SMS message
          * **address:** sender phone number
          * **date:** when sms was received
          * **status:** SMS status report if supported, None otherwise
        """
        message = []
        while(not self.recv_queue.empty()):
            message.append(self.recv_queue.get())
        return message

    def stop(self):
        """
        Stop
        """
        pass
