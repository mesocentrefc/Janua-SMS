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

"""
========================  ================  ==========================
Location                  Methods           Authorized roles
========================  ================  ==========================
/api/ACTION               GET, PUT          admin, supervisor
========================  ================  ==========================
"""

from flask_restless import ProcessingException

from janua.ws.api.base import BaseApi
from janua.utils.utilities import get_role
from janua.ws.api.db import get_action_ids

from janua.db.database import Action as ActionTable

class Action(BaseApi):
    """
    Action REST API
    
    Expose database object: :class:`Action <janua.db.database.Action>`

    """
    methods = ['GET', 'PUT']
    authorized_roles = ['admin', 'supervisor']
    model = ActionTable

    exclude_columns = [
        'module',
        'janua_id',
        'authorized_supervisor.password',
        'authorized_supervisor.phone_token',
        'authorized_supervisor.web_auth_token',
        'admin.password',
        'admin.phone_token',
        'admin.web_auth_token'
    ]

    @staticmethod
    def get_single_preprocessor(admin, instance_id=None, **kw):
        """Accepts a single argument, `instance_id`, the primary key of the
        instance of the model to get.

        """
        if get_role(admin) != 'admin':
            if instance_id and int(instance_id) not in get_action_ids(admin):
                raise ProcessingException(description='', code=404)

    @staticmethod
    def get_many_preprocessor(admin, search_params=None, **kw):
        """Accepts a single argument, `search_params`, which is a dictionary
        containing the search parameters for the request.

        """
        if get_role(admin) != 'admin':
            if 'filters' in search_params:
                search_params['filters'].append({
                    u'name': u'admin_id', u'op': u'eq', u'val': admin.id
                })
            else:
                search_params.update({
                    'filters': [{
                        u'name': u'admin_id',
                        u'op': u'eq',
                        u'val': admin.id
                    }]
                })

    @staticmethod
    def patch_single_preprocessor(admin, instance_id=None, data=None, **kw):
        """Accepts two arguments, `instance_id`, the primary key of the
        instance of the model to patch, and `data`, the dictionary of fields
        to change on the instance.

        """
        if get_role(admin) == 'admin':
            if 'admin_id' not in data:
                raise ProcessingException(description='', code=400)
            else:
                keys = [key for key in data]
                for key in keys:
                    if key != 'admin_id':
                        data.pop(key, None)
        else:
            raise ProcessingException(description='', code=405)
