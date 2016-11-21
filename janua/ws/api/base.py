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

from flask_restless import ProcessingException

from janua.ws.auth import auth_required

def register_api(manager, api):
    reg_api = api()
    model, kwargs = reg_api.get_args()
    manager.create_api(model, **kwargs)

class BaseApi(object):
    model = None
    results_per_page = 10000
    max_results_per_page = 10000
    methods = ['GET','POST','PUT']
    authorized_roles = ['admin']
    exclude_columns = None

    def __init__(self):
        preprocessors_methods = [
            'get_single_preprocessor',
            'get_many_preprocessor',
            'patch_single_preprocessor',
            'patch_many_preprocessor',
            'post_preprocessor',
            'delete_single_preprocessor',
            'delete_many_preprocessor',
        ]

        self.preprocessors = {}
        for preprocessor in preprocessors_methods:
            key = preprocessor.split('_preprocessor')[0].upper()
            preproc = getattr(self, preprocessor, None)
            if key not in self.preprocessors:
                self.preprocessors.update({key: []})
            if preproc:
                auth_preproc = auth_required(role=self.authorized_roles, rest_api=True)(preproc)
                self.preprocessors[key].append(auth_preproc)

        self.restless_kwargs = {
            'results_per_page': self.results_per_page,
            'max_results_per_page': self.max_results_per_page,
            'preprocessors': self.preprocessors,
            'exclude_columns': self.exclude_columns,
            'methods': self.methods
        }

    def get_args(self):
        return self.model, self.restless_kwargs

    @staticmethod
    def get_single_preprocessor(admin, instance_id=None, **kw):
        pass

    @staticmethod
    def get_many_preprocessor(admin, search_params=None, **kw):
        pass

    @staticmethod
    def patch_single_preprocessor(admin, instance_id=None, data=None, **kw):
        pass

    @staticmethod
    def post_preprocessor(admin, data=None, **kw):
        pass

    @staticmethod
    def delete_single_preprocessor(admin, instance_id=None, **kw):
        pass

    @staticmethod
    def patch_many_preprocessor(admin, search_params=None, data=None, **kw):
        pass

    @staticmethod
    def delete_many_preprocessor(admin, search_params=None, **kw):
        pass
