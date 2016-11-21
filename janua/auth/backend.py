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
To implement your own authentication backend, you must inherit from
AuthBackend object.

Put your authentication backend module in **/opt/janua/custom/auth** directory

**Example with local backend:**

.. code-block:: python

   class Local(AuthBackend):
       def authenticate_admin(self, admin, password):
           if not check_password(admin.password, password):
               raise AuthError('Bad password for %s' % admin.login)
"""

from janua.utils.utilities import get_subclasses
from janua.auth import AuthError, AuthConfigError

class AuthBackendManager(object):
    def __init__(self):
        self._pool_backend = {}
        self._pool_backend_name = []

    def register(self, db):
        for cls in get_subclasses(AuthBackend):
            backend = cls(db)
            name = backend.name
            self._pool_backend.update({name: backend})
            self._pool_backend_name.append(name)

    def get(self, name):
        if name in self._pool_backend_name:
            return self._pool_backend[name]

    def list(self):
        return self._pool_backend_name

class AuthBackend(object):
    """
    Authentication backend object and implement :meth:`.authenticate_admin`
    method
    """

    config = []
    """
    List of configuration parameters, each parameters specify:

    * **description:** a short description
    * **name:** key name to identify it in :class:`Config <janua.db.database.Config>` table
    * **type:** type of parameter, possible types: **string, boolean, interger**
    * **value:** parameter's value

    .. warning::
    
       Don't put spaces in name as it will be converted to class attributes
       when backend object is instanciated

    **Example:**

    .. code-block:: python

       config = [
           {
               'description': 'Uri',
               'name': 'ldap_uri',
               'type': 'string',
               'value': 'ldap://127.0.0.1:389'
           },
           {
               'description': 'Bind DN',
               'name': 'ldap_bind_dn',
               'type': 'string',
               'value': 'uid=${login},ou=people,dc=organization,dc=com'
           },
           {
               'description': 'TLS support',
               'name': 'ldap_tls_support',
               'type': 'boolean',
               'value': False
           }
       ]

    """

    help = None
    """
    Help in HTML format which will be displayed in web interface
    
    **Example:**

    .. code-block:: python

       help = \"\"\"
       LDAP configuration help
       <ul>
       <li>Uri: ldap uri</li>
       <li>Bind DN: user DN, where ${login} will be replaced with corresponding login</li>
       <li>TLS support: enable TLS connection</li>
       </ul>
       \"\"\"
    """

    mail_template_creation = 'create_admin'
    """Mail template to use when an account is created to use this backend"""

    def __init__(self, db):
        self.name = self.__class__.__name__.lower()
        self.db = db
        self._params = []
        for cfg in self.config:
            if 'name' not in cfg:
                raise AuthConfigError(
                    'parameter name is missing in %s auth backend' % self.name
                )
            name = cfg['name']
            self._params.append(name)
            if 'description' not in cfg:
                raise AuthConfigError(
                    'parameter description is missing for %s in %s auth backend' % (name, self.name)
                )
            if 'value' not in cfg:
                raise AuthConfigError(
                    'parameter value is missing for %s in %s auth backend' % (name, self.name)
                )
            if 'type' not in cfg:
                raise AuthConfigError(
                    'parameter type is missing for %s in %s auth backend' % (name, self.name)
                )
            entry = self.db.config.get(name)
            if entry:
                value = entry.value
                self.config[self._params.index(name)]['value'] = value
            else:
                value = cfg['value']
            setattr(self, name, value)

    def update_config(self, config):
        """
        Configure backend in database. Raise a
        :class:`janua.auth.AuthConfigError` exception if configure failed in
        database
        
        .. note::
           You don't have to implement this method in your backend

        :param config: a dictionary corresponding to configuration parameters
        """
        for param, value in config.items():
            entry = self.db.config.get(param)
            if entry:
                entry.value = value
                if not self.db.update_entry(entry):
                    raise AuthConfigError('failed to set %s value' % param)
            else:
                if param not in self._params:
                    raise AuthConfigError('%s is not a parameter' % param)
                if not self.db.config.add(param, value):
                    raise AuthConfigError('failed to add %s in database' % param)
            setattr(self, param, value)
            self.config[self._params.index(param)]['value'] = value

    def authenticate_admin(self, admin, password):
        """
        Authenticate users.
        
        This method doesn't return anything, so in case of authentication
        error, you must raise :class:`janua.auth.AuthError` exception

        :param admin: admin database object (:class:`janua.db.database.Admin`)
        :param password: user password
        """
        raise AuthError('Not supported')
