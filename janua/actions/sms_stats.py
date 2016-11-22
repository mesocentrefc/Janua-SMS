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

class SmsStats(Action):
    """
    Get SMS month statistics for the current year

    Sample request:

    .. code-block:: javascript

       GET /sms-stats HTTP/1.1
       Host: janua.mydomain.com
       Content-Type: application/json
       JanuaAuthToken: abcdef123456789

    Sample response:

    .. code-block:: javascript

       HTTP/1.1 200

       {
         "num_results": 12, 
         "objects": [
           {
             "month": "Jan", 
             "value": 0
           }, 
           {
             "month": "Feb", 
             "value": 0
           }, 
           {
             "month": "Mar", 
             "value": 0
           }, 
           {
             "month": "Apr", 
             "value": 0
           }, 
           {
             "month": "May", 
             "value": 0
           }, 
           {
             "month": "Jun", 
             "value": 0
           }, 
           {
             "month": "Jul", 
             "value": 0
           }, 
           {
             "month": "Aug", 
             "value": 0
           }, 
           {
             "month": "Sep", 
             "value": 0
           }, 
           {
             "month": "Oct", 
             "value": 18
           }, 
           {
             "month": "Nov", 
             "value": 0
           }, 
           {
             "month": "Dec", 
             "value": 0
           }
         ]
       }

    """

    category = '__INTERNAL__'

    @urlconfig('/sms-stats')
    def web(self):
        admin = jdb.admin.get_by_phone(self.phone_number)
        data = jdb.sms.get_admin_month_stats(admin)
        return jsonify(num_results=len(data), objects=data)
