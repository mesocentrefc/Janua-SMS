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
======================  ===================  ==========================
Location                Methods              Authorized roles
======================  ===================  ==========================
/api/SMS                GET                  admin, supervisor
======================  ===================  ==========================
"""

from flask_restless import ProcessingException

from janua.ws.api.base import BaseApi

from janua.db.database import Sms as SmsTable

class Sms(BaseApi):
    """
    Sms REST API
    
    Expose database object: :class:`Sms <janua.db.database.Sms>`
    """
    methods = ['GET']
    model = SmsTable
    authorized_roles = ['admin', 'supervisor']
    exclude_columns = ['reference', 'admin_id']

    @staticmethod
    def get_single_preprocessor(admin, instance_id=None, **kw):
        """Accepts a single argument, `instance_id`, the primary key of the
        instance of the model to get.

        """
        raise ProcessingException(description='Not supported', code=404)

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
