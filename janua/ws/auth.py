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

import os
import base64
from datetime import timedelta

from flask import abort, request
from functools import wraps

from itsdangerous import TimedJSONWebSignatureSerializer as TimedSerializer
from itsdangerous import JSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

from flask_restless import ProcessingException

import janua.utils.logger as jlogger

from janua import config, jdb, januapath
from janua.utils.utilities import extract_group_number_and_mail
from janua.utils.utilities import import_available_modules
from janua.utils.utilities import get_role
from janua.utils import exit_error

from janua.auth import AuthError, AuthConfigError
from janua.auth.backend import AuthBackendManager
from janua.auth.local_backend import Local
try:
    from janua.auth.ldap_backend import Ldap
except ImportError:
    # simply ignore if something failed
    pass

try:
    import_available_modules('custom.auth', januapath)
except Exception, err:
    exit_error('Failed to import custom auth backend', traceback=True)

log = jlogger.getLogger(__name__)

secret_key = jdb.config.get('flask_secret_key')
if secret_key == None:
    flask_secret_key = base64.b64encode(os.urandom(64))
    jdb.config.add('flask_secret_key', flask_secret_key)
else:
    flask_secret_key = secret_key.value

def get_token_serializer(expires_in=None):
    if expires_in:
        return TimedSerializer(flask_secret_key, expires_in=expires_in)
    else:
        return Serializer(flask_secret_key)

token_serializer = get_token_serializer(
    expires_in=timedelta(hours=config.web.session_lifetime).seconds
)
one_minute_token_serializer = get_token_serializer(expires_in=60)

auth_manager = AuthBackendManager()
try:
    auth_manager.register(jdb)
except AuthConfigError, err:
    exit_error(err)

def deserialize_token(token):
    """
    Deserialize token

    :param token: token to deserialize
    :returns: deserialized data or None if bad token
    """
    try:
        data = token_serializer.loads(token)
    except (SignatureExpired, BadSignature):
        return None

    return data

def serialize_token(admin_id, serializer=one_minute_token_serializer):
    """
    Serialize token

    :param admin_id: admin database id
    :param serializer: serializer to use
    :returns: serialized data or None if serialization failed
    """
    try:
        admin_id = int(admin_id)
    except ValueError:
        return None

    admin = jdb.admin.get_by_id(admin_id)
    if not admin:
        return None

    if admin.web_auth_token == None:
        admin.web_auth_token = base64.b64encode(os.urandom(96))
        if not jdb.update_entry(admin):
            return None

    return serializer.dumps({'id': admin_id, 'token': admin.web_auth_token})

def authenticate_admin(username, password):
    """
    Authenticate admin / supervisor

    :param username: username
    :param password: password
    :returns: admin database entry corresponding to credentials or None if authentication failed
    """
    login, phone, _ = extract_group_number_and_mail(username)

    if login:
        admin = jdb.admin.get_by_login(login[0])
        if not admin:
            return None
        backend = auth_manager.get(admin.auth_backend)
    elif phone:
        admin = jdb.admin.get_by_phone(phone[0])
        if not admin:
            return None
        backend = auth_manager.get('local')
    else:
        return None

    try:
        backend.authenticate_admin(admin, password)
    except AuthError, err:
        log.error(err)
        return None

    return admin

def validate_auth(role):
    """
    Check if admin / supervisor credentials are valid

    :param role: a list of authorized roles
    :returns: admin database entry or None if validation failed
    """
    auth_token = request.headers.get('JanuaAuthToken')
    if auth_token:
        data = deserialize_token(auth_token)
        if not data:
            return None

        admin = jdb.admin.get_by_id(data['id'])
        if not admin:
            return None

        if get_role(admin) not in role:
            return None

        if admin.web_auth_token == data['token']:
            return admin

    auth = request.authorization
    if auth:
        username = auth.username
        password = auth.password
        admin = authenticate_admin(username, password)
        if not admin:
            return None

        if get_role(admin) in role:
            return admin

    return None

def auth_required(role, rest_api=False, action_name=None):
    """
    Authentication decorator for flask route url and Rest API

    :param role: a list of authorized roles
    :param rest_api: used in Flask-Restless API context
    :param action_name: if used in action context, should contain action name
    """
    def check_role(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            admin = validate_auth(role)
            if admin:
                if action_name:
                    return f(admin, action_name, *args, **kwargs)
                else:
                    return f(admin, *args, **kwargs)
            if rest_api:
                raise ProcessingException(description='Not Authorized', code=401)
            else:
                abort(401)
        return decorated
    return check_role
