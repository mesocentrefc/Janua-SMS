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

from flask import jsonify

import janua.utils.logger as jlogger

from janua import jdb
from janua.actions.action import Action
from janua.ws.services import get_url
from janua.utils.pwgen import pwgen

log = jlogger.getLogger(__name__)

class GetConfig(Action):
    """
    Get config
    """

    category = '__INTERNAL__'

    def sms(self):
        admin = jdb.admin.get_by_phone(self.phone_number)
        if admin:
            if admin.has_client == False:
                admin.has_client = True
                admin.phone_token = pwgen(pw_length=8, num_pw=1, capitalize=True, no_symbols=True)
                if jdb.update_entry(admin):
                    log.info('Contact %s %s seems to have Janua client, '
                              'has_client flag was set'
                              % (admin.firstname, admin.name))
                else:
                    log.error('Failed to set has_client flag for contact '
                               '%s %s' % (admin.firstname, admin.name))
                    self.notify.sms.sender('An error occured while updating '
                                          'your informations. Please '
                                          'contact Janua administrator')
                    return

            self.notify.sms.sender('1:%s' % (get_url() + 'get_sms_config'))
        else:
            log.info('Someone (%s) try to get sms config' % self.phone_number)
