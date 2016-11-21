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

import ldap

from string import Template

import janua.utils.logger as jlogger

from janua.auth import AuthError
from janua.auth.backend import AuthBackend

log = jlogger.getLogger(__name__)

class Ldap(AuthBackend):
    mail_template_creation = 'create_admin_ldap'

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

    help = """
    LDAP configuration help
    <ul>
    <li>Uri: ldap uri</li>
    <li>Bind DN: user DN, where ${login} will be replaced with corresponding login</li>
    <li>TLS support: enable TLS connection</li>
    </ul>
    """

    def authenticate_admin(self, admin, password):
        username = admin.login
        d = dict(login=username)
        try:
            dn = Template(self.ldap_bind_dn).substitute(d)
        except (KeyError, ValueError), err:
            raise AuthError('Check bind DN parameter')

        log.debug('%s open ldap connection %s' % (username, self.ldap_uri))
        try:
            if self.ldap_tls_support:
                # yeah it's a bad practice, exercice is left to the reader ...
                ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            l = ldap.initialize(self.ldap_uri)
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            if self.ldap_tls_support:
                l.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
                l.start_tls_s()
        except:
            raise AuthError('Failed to connect to ldap server: %s' % err)

        try:
            l.simple_bind_s(dn, password)
        except ldap.INVALID_CREDENTIALS:
            l.unbind_s()
            raise AuthError('Failed to authenticate %s' % username)
