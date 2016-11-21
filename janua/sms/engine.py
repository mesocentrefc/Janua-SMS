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
"""
If you want to add a new SMS engine, you must inherit from SMSEngine object and
implement all methods describe below.

Put your SMS engine in **/opt/janua/custom/engine** directory and restart
Janua-SMS

**Example:**

.. code-block:: python

   config_spec = \"\"\"
   #
   # android section
   #
   [android]
   message_timeout = integer(1000, 30000, default=1000)
   \"\"\"

   class AndroidSMS(SMSEngine):
       \"\"\"Android SMS class interface\"\"\"
       name = 'android'
       config_spec = config_spec
    
       def __init__(self, config):
           log.debug('message timeout: %d ms' % config.android.message_timeout)
    
       def reconnect(self, event):
           pass

       ...
"""
import time

class SMSEngine(object):
    """
    Abstract class for SMS interface
    """

    name = None
    """Engine name"""

    config_spec = None
    """
    Configuration specification for this engine. You can refer to `configobj documentation <http://www.voidspace.org.uk/python/configobj.html#configspec>`_
    """

    def __init__(self, config):
        """
        Engine initialization

        :param config: global configuration object
        """
        raise NotImplementedError('__init__ method is missing')

    def reconnect(self, event):
        """
        Try to connect to modem or service in case of communication error

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
        raise NotImplementedError('Not supported')

    def event(self):
        """
        Listen event

        :returns: True when a message is received or False when there is no message
        """
        raise NotImplementedError('Not supported')

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
        raise NotImplementedError('Not supported')

    def stop(self):
        """
        Stop
        """
        raise NotImplementedError('Not supported')
