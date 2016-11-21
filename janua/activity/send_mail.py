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

import Queue

import janua.utils.logger as jlogger

from janua import mail_queue, januapath
from janua.activity.activity import Activity
from janua.utils.mail import MailError
from janua.utils.mail import JanuaMailer, MailObj

log = jlogger.getLogger(__name__)

class SendMailActivity(Activity):
    """
    Mail sender activity
    """
    def __init__(self, config, *args, **kwargs):
        super(SendMailActivity, self).__init__(*args, **kwargs)
        self.mailer = JanuaMailer(config, januapath)
        self.config = config

    def run(self):
        while not self._stopevent.isSet():
            try:
                mailobj = mail_queue.get(True, 1)
            except Queue.Empty:
                continue

            try:
                if self.mailer.sendmail(mailobj):
                    if isinstance(mailobj.to, list):
                        log.info('Sending mail to %s' % ', '.join(mailobj.to))
                    else:
                        log.info('Sending mail to %s' % mailobj.to)
                else:
                    if isinstance(mailobj.to, list):
                        log.error('Failed to send mail to %s' % ', '.join(mailobj.to))
                    else:
                        log.error('Failed to send mail to %s' % mailobj.to)
            except MailError, err:
                log.error('Failed to send mail: %s' % err[0])
                if self.config.enable == True:
                    mail_queue.put(mailobj)
