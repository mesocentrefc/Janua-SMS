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

from janua import jdb
from janua.actions.action import Action
from janua.utils.utilities import get_role
from janua.ws.services import urlconfig, jsonify

class SmsUsage(Action):
    """
    Get SMS usage based on administrator quota

    * Sample request with administrator level:

      .. code-block:: javascript

         GET /sms-usage HTTP/1.1
         Host: janua.mydomain.com
         Content-Type: application/json

      Sample response:

      .. code-block:: javascript

         HTTP/1.1 200

         {
           "smsusage": {
             "global": 18, 
             "quota": "100 M", 
             "sent": 18
           }
         }

    * Sample request with supervisor level:

      .. code-block:: javascript

         GET /sms-usage HTTP/1.1
         Host: janua.mydomain.com
         Content-Type: application/json

      Sample response:

      .. code-block:: javascript

         HTTP/1.1 200

         {
           "smsusage": {
             "quota": "200 D", 
             "sent": 4
           }
         }

    """

    category = '__INTERNAL__'

    @urlconfig('/sms-usage')
    def web(self):
        admin = jdb.admin.get_by_phone(self.phone_number)
        data = {
            'success': True,
            'params': [],
            'num_params': 0
        }
        reached, numsms = jdb.sms.is_admin_quota_reached(admin)
        quota = admin.sms_quota
        data = {'sent': int(numsms), 'quota': quota}
        if get_role(admin) == 'admin':
            data.update({'global': int(jdb.sms.month_usage())})
        return jsonify(smsusage=data)
