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
/api/CONTACT              GET, POST, PUT, DELETE          admin, supervisor
========================  ==============================  ==========================
"""

from janua import config

from flask_restless import ProcessingException

from janua import config
from janua.utils.utilities import valid_prefix_number
from janua.ws.api.base import BaseApi
from janua.ws.auth import get_role
from janua.ws.api.db import get_contact_ids

from janua.db.database import Contact as ContactTable

class Contact(BaseApi):
    """
    Contact REST API
    
    Expose database object: :class:`Contact <janua.db.database.Contact>`
    """
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    authorized_roles = ['admin', 'supervisor']
    model = ContactTable

    @staticmethod
    def get_single_preprocessor(admin, instance_id=None, **kw):
        """Accepts a single argument, `instance_id`, the primary key of the
        instance of the model to get.

        """
        if instance_id and int(instance_id) not in get_contact_ids(admin):
            raise ProcessingException(description='', code=404)

    @staticmethod
    def get_many_preprocessor(admin, search_params=None, **kw):
        """Accepts a single argument, `search_params`, which is a dictionary
        containing the search parameters for the request.

        """
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
        if instance_id and int(instance_id) not in get_contact_ids(admin):
            raise ProcessingException(description='', code=404)
        if 'phone_number' in data:
            if not valid_prefix_number(data['phone_number'], config.sms.prefix_filter):
                raise ProcessingException(description='Phone number prefix not allowed', code=422)

    @staticmethod
    def post_preprocessor(admin, data=None, **kw):
        """Accepts a single argument, `data`, which is the dictionary of
        fields to set on the new instance of the model.

        """
        if 'admin_id' not in data:
            data.update({'admin_id': admin.id})
        elif data['admin_id'] != admin.id:
            data['admin_id'] = admin.id
        if 'phone_number' in data:
            if not valid_prefix_number(data['phone_number'], config.sms.prefix_filter):
                raise ProcessingException(description='Phone number prefix not allowed', code=400)

    @staticmethod
    def delete_single_preprocessor(admin, instance_id=None, **kw):
        """Accepts a single argument, `instance_id`, which is the primary key
        of the instance which will be deleted.

        """
        if instance_id and int(instance_id) not in get_contact_ids(admin):
            raise ProcessingException(description='', code=404)
