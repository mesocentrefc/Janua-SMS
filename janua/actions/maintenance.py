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

import janua.utils.logger as jlogger

from janua.actions.action import Action, argument, date, console_success
from janua.utils.mail import MailObj, MailError

log = jlogger.getLogger(__name__)

class Maintenance(Action):
    """
    Send maintenance mail
    """
    category = '__INTERNAL__'

    def console(self):
        template = 'maintenance'
        template_args = {
            'startdate': self.start_date(),
            'starttime': self.start_time(),
            'duration': self.duration(),
        }
        try:
            mailobj = MailObj()
            mailobj.template = template
            mailobj.template_args = template_args
        except MailError, err:
            log.error('Cannot instanciate mail object')

        self.notify.mail.supervisors(template=template, template_args=template_args)
        self.notify.sms.supervisors('Maintenance')
        return console_success('Supervisor has been informed of maintenance operation')

    @argument(required=True)
    def start_date(self):
        """From date (date format: YYYY/MM/DD)"""
        return date()

    @argument(required=True)
    def start_time(self):
        """From time"""
        return str()

    @argument(required=True)
    def duration(self):
        """Maintenance duraction in hour"""
        return int()
