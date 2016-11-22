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
from janua.ws.services import urlconfig, jsonify
from janua.ws.auth import auth_manager

class ListAuthBackend(Action):
    """
    Get the a list of available authentication backends
    
    Sample request:

    .. code-block:: rest

       GET /list_auth_backend HTTP/1.1
       Host: janua.mydomain.com
       Content-Type: application/json
       JanuaAuthToken: abcdef123456789

    Sample response:

    .. code-block:: javascript

       HTTP/1.1 200

       {
         "backends": [
           {
             "name": "local"
           }, 
           {
             "name": "ldap"
           }
         ], 
         "num_backends": 2
       }

    """

    category = '__INTERNAL__'

    @urlconfig('/list_auth_backend', role=['admin'])
    def web(self):
        backends = [{'name': name} for name in auth_manager.list()]
        data = {
            'backends': backends,
            'num_backends': len(backends)
        }
        return jsonify(**data)
