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

from janua.actions.action import Action
from janua.utils.utilities import doctrim
from janua.ws.services import urlconfig, jsonify
from janua.ws.auth import auth_manager

class GetAuthBackend(Action):
    """Get authentication backend configuration

    Sample request to LDAP backend configuration:

    .. code-block:: rest

       GET /get_auth_backend/ldap HTTP/1.1
       Host: janua.mydomain.com
       Content-Type: application/json
       JanuaAuthToken: abcdef123456789

    Sample response:

    .. code-block:: javascript

       HTTP/1.1 200

       {
         "help": "Ldap help in html format", 
         "num_params": 3, 
         "params": [
           {
             "description": "Uri", 
             "name": "ldap_uri", 
             "type": "string", 
             "value": "ldap://ldap.example.fr:389"
           }, 
           {
             "description": "Bind DN", 
             "name": "ldap_bind_dn", 
             "type": "string", 
             "value": "uid=${login},ou=people,dc=example,dc=fr"
           },
           {
             "description": "TLS support", 
             "name": "ldap_tls_support", 
             "type": "boolean", 
             "value": "1"
           }
         ], 
         "success": true
       }

    """

    category = '__INTERNAL__'

    @urlconfig('/get_auth_backend/<backend>', role=['admin'])
    def web(self, backend):
        data = {
            'success': True,
            'params': [],
            'num_params': 0,
            'help': None
        }
        auth_backend = auth_manager.get(backend)
        if auth_backend:
            data['params'] = auth_backend.config
            data['num_params'] = len(auth_backend.config)
            if auth_backend.help:
                data['help'] = doctrim(auth_backend.help)
        else:
            data['success'] = False
        return jsonify(**data)
