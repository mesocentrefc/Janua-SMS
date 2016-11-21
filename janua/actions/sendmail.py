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

import json

from janua.actions.action import Action
from janua.actions.action import argument
from janua.ws import json_error, json_success
from janua.ws.services import urlconfig

class SendMail(Action):
    """
    Send mail

    * Send simple mail to all my contacts:

      .. code-block:: javascript

         POST /sendmail HTTP/1.1
         Host: janua.mydomain.com
         Content-Type: application/json

         {
           "message": "A simple test message",
           "subject": "Simple test",
           "to": "all"
         }

      Sample response:

      .. code-block:: javascript

         HTTP/1.1 200

         {
           "message": "SMS message has been queued",
           "success": true
         }

    * Send templated mail to all my contacts (see :ref:`mail templates <mail_templates>`):

      .. code-block:: javascript

         POST /sendmail HTTP/1.1
         Host: janua.mydomain.com
         Content-Type: application/json

         {
           "to": "all",
           "template": "mytemplate",
           "template_args:
           {
             "first_arg": "first argument",
             "second_arg": "second argument"
           }
         }

      Sample response:

      .. code-block:: javascript

         HTTP/1.1 200

         {
           "message": "SMS message has been queued",
           "success": true
         }

    """

    category = '__INTERNAL__'

    @urlconfig('/sendmail')
    def web(self):
        if self.template_args():
            template_args = json.loads(self.template_args())
        else:
            template_args = {}

        success, message = self.send_email(
            subject=self.subject(),
            message=self.message(),
            to=self.to(),
            template=self.template(),
            template_args=template_args
        )
        if success:
            return json_success(message)
        else:
            return json_error(message)

    @argument(required=False)
    def subject(self):
        """Mail subject"""
        return str()

    @argument(required=False)
    def message(self):
        """Mail body"""
        return str()

    @argument(required=True)
    def to(self):
        """Recipient(s)"""
        return str()

    @argument(required=False)
    def template(self):
        """Mail template"""
        return str()

    @argument(required=False)
    def template_args(self):
        """Mail template arguments in JSON format"""
        return str()
