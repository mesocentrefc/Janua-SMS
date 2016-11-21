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
from janua.ws.auth import auth_manager, AuthConfigError

class SetAuthBackend(Action):
    """
    Set authentication backend configuration

    Sample request to set configuration for LDAP backend:

    .. code-block:: javascript

       POST /set_auth_backend/ldap HTTP/1.1
       Host: janua.mydomain.com
       Content-Type: application/json

       {
         "parameters":
         {
           "ldap_uri": "ldap://ldap.example.fr:389", 
           "ldap_bind_dn": "uid=${login},ou=people,dc=example,dc=fr", 
           "ldap_tls_support": false
         }, 
         "success": true
       }

    Sample response:

    .. code-block:: javascript

       HTTP/1.1 200

       {
         "message": "Configuration has been saved",
         "success": true
       }

    """

    category = '__INTERNAL__'

    @urlconfig('/set_auth_backend/<backend>', role=['admin'])
    def web(self, backend):
        auth_backend = auth_manager.get(backend)
        if auth_backend:
            try:
                auth_backend.update_config(self.parameters())
            except AuthConfigError, err:
                return json_error('Failed to update configuration: %s' % err)
        return json_success('Configuration has been saved')

    @argument(required=True)
    def parameters(self):
        """Backend config parameters"""
        return str()
