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
========================  ==============================  ==========================
Location                  Methods                         Authorized roles
========================  ==============================  ==========================
/api/ADMIN                GET, POST, PUT, DELETE          admin, supervisor
========================  ==============================  ==========================
"""

from janua import config

from flask_restless import ProcessingException

from janua.ws.api.base import BaseApi
from janua.ws.auth import get_role
from janua.utils.utilities import valid_prefix_number, hash_password

from janua.db.database import Admin as AdminTable

class Admin(BaseApi):
    """
    Admin REST API
    
    Expose database object: :class:`Admin <janua.db.database.Admin>`
    """
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    authorized_roles = ['admin', 'supervisor']
    model = AdminTable
    exclude_columns= [
        'password',
        'phone_token',
        'web_auth_token'
    ]

    @staticmethod
    def get_single_preprocessor(admin, instance_id=None, **kw):
        """Accepts a single argument, `instance_id`, the primary key of the
        instance of the model to get.

        """
        if instance_id:
            if int(instance_id) != admin.id and get_role(admin) != 'admin':
                raise ProcessingException(description='', code=404)

    @staticmethod
    def get_many_preprocessor(admin, search_params=None, **kw):
        """Accepts a single argument, `search_params`, which is a dictionary
        containing the search parameters for the request.

        """
        if get_role(admin) != 'admin':
            if 'filters' in search_params:
                search_params['filters'].append({
                    u'name': u'id', u'op': u'eq', u'val': admin.id
                })
            else:
                search_params.update({
                    'filters': [{
                        u'name': u'id',
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
        if instance_id:
            if int(instance_id) != admin.id and get_role(admin) != 'admin':
                raise ProcessingException(description='', code=404)
            # enforce access level
            if get_role(admin) == 'supervisor':
                if 'phone_number' in data:
                    raise ProcessingException(description='You don\'t have permission to change your phone_number', code=401)
                if 'level' in data and data['level'] != 2:
                    raise ProcessingException(description='You don\'t have permission to change your access level', code=401)
                # special case: supervisor ask for changing sms quota
                if 'sms_quota' in data:
                    data['sms_quota'] = '!%s' % data['sms_quota']
                if 'recipient_filter' in data:
                    raise ProcessingException(description='You don\'t have permission to change sms recipient filter', code=401)
                if 'login' in data:
                    raise ProcessingException(description='You don\'t have permission to change your login', code=401)
                if 'auth_backend' in data:
                    raise ProcessingException(description='You don\'t have permission to change your authentication backend', code=401)
            else:
                if admin.id == int(instance_id) and 'auth_backend' in data and data['auth_backend'] != 'local':
                    raise ProcessingException(description='Administrator must be a local account')
            if 'password' in data:
                data['password'] = hash_password(data['password'])
            if 'phone_number' in data:
                if not valid_prefix_number(data['phone_number'], config.sms.prefix_filter):
                    raise ProcessingException(description='Phone number prefix not allowed', code=422)

    @staticmethod
    def post_preprocessor(admin, data=None, **kw):
        """Accepts a single argument, `data`, which is the dictionary of
        fields to set on the new instance of the model.

        """
        if get_role(admin) != 'admin':
            raise ProcessingException(description='', code=405)
        else:
            if 'level' not in data:
                data.update({'level': 2})
            else:
                data['level'] = 2
            if 'password' not in data:
                raise ProcessingException(description='Password is missing', code=405)
            if 'phone_number' in data:
                if not valid_prefix_number(data['phone_number'], config.sms.prefix_filter):
                    raise ProcessingException(description='Phone number prefix not allowed', code=400)

    @staticmethod
    def delete_single_preprocessor(admin, instance_id=None, **kw):
        """Accepts a single argument, `instance_id`, which is the primary key
        of the instance which will be deleted.

        """
        if get_role(admin) != 'admin':
            raise ProcessingException(description='Not authorized', code=405)
