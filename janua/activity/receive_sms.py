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

import time

import janua.utils.logger as jlogger

from janua.activity.activity import Activity
from janua.sms import SMSError, ModemError

log = jlogger.getLogger(__name__)

class ReceiveSmsActivity(Activity):
    """
    SMS receiver activity
    """
    def __init__(self, sms_interface, queue_process, *args, **kwargs):
        super(ReceiveSmsActivity, self).__init__(*args, **kwargs)
        self._sms = sms_interface
        self._process_queue = queue_process

    def run(self):
        while not self._stopevent.isSet():
            try:
                if self._sms.event():
                    self._process_queue.put('message received')
            except SMSError, err:
                log.error(err)
            except ModemError, err:
                log.critical(err)
                self._sms.reconnect(self._stopevent)

    def stop(self):
        super(ReceiveSmsActivity, self).stop()
        try:
            self._sms.stop()
        except ModemError, msg:
            log.error(msg)
