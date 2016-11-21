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

import calendar
import os
import uuid

from flask import __version__ as flask_version
from flask import Flask, jsonify
from flask import make_response, request, url_for
from flask import redirect, render_template

from flask_restless import APIManager

from datetime import timedelta, datetime

from janua import config, jdb, januapath
from janua.actions import ActionError, ActionNotifyError
from janua.actions.action import available_action_dict, get_custom_action_repr
from janua.actions.action import WebInit
from janua.utils.utilities import get_role

from janua.ws import json_error, json_success
from janua.ws.auth import serialize_token, token_serializer
from janua.ws.auth import flask_secret_key, auth_manager
from janua.ws.auth import auth_required, authenticate_admin

#
# REST API
#
from janua.ws.api.base import register_api
from janua.ws.api.sms import Sms
from janua.ws.api.contact import Contact
from janua.ws.api.group import Group
from janua.ws.api.contact_group import ContactGroup
from janua.ws.api.admin import Admin
from janua.ws.api.action import Action
from janua.ws.api.authorized_group_action import AuthorizedGroupAction
from janua.ws.api.authorized_supervisor_action import AuthorizedSupervisorAction
from janua.ws.api.contact_notify_action import ContactNotifyAction

static_folder = os.path.join(januapath, 'janua-web')
app = Flask(__name__, static_url_path='', static_folder=static_folder)
app.secret_key = flask_secret_key

manager = APIManager(app, session=jdb.session)
register_api(manager, Sms)
register_api(manager, Contact)
register_api(manager, Group)
register_api(manager, ContactGroup)
register_api(manager, Admin)
register_api(manager, Action)
register_api(manager, AuthorizedGroupAction)
register_api(manager, AuthorizedSupervisorAction)
register_api(manager, ContactNotifyAction)

def action(admin, action_name, *args, **kwargs):
    """
    Action wrapper for web context
    """
    action_dict = available_action_dict(include_keyword=False)

    arguments = {}
    if not request.json and request.method == 'POST':
        return json_error('Not in json format')
    if request.method == 'POST':
        arguments = request.json

    try:
        action = action_dict[action_name]()
        action.phone_number = admin.phone_number
        action.email = admin.email
        ret = action.call_web_context(arguments, *args, **kwargs)
    except ActionError, err:
        return json_error('Failed to trigger action: %s' % err)
    except (ValueError, TypeError):
        return json_error('web context method for %s return an invalid value' % action_name)
    except ActionNotifyError, err:
        return json_error('Notify method failed: %s' % err)
    except Exception, err:
        return json_error('Bug in action %s: %s' % (action.get_name(), err))

    error_msg = action.process_notify()
    del action
    if error_msg:
        return json_error(error_msg)

    return ret

def urlconfig(url, role=['admin', 'supervisor']):
    """
    Web action context decorator

    :param url: relative url (ex: /login)
    :param role: list of authorized role, by default all are authorized
    """
    def wrap(func):
        def init_callback(action_name, method):
            app.add_url_rule(
                url,
                action_name,
                auth_required(role=role, action_name=action_name)(action),
                methods=[method]
            )
        return WebInit(func, init_callback)
    return wrap

def get_url():
    """
    Get Janua-SMS url

    :returns: janua url
    """
    if config.web.url:
        if config.web.url[-1] != '/':
            return '%s/' % config.web.url
        return config.web.url

    port = int(config.web.port)
    hostname = config.web.hostname
    if config.web.secure_connection:
        url = 'https://'
    else:
        url = 'http://'

    if port != 443 or port != 80:
        url += '%s:%s/' % (hostname, port)
    else:
        url += '%s/' % hostname

    return url

@app.route('/')
def root():
    """
    Web server root
    """
    if config.web.secure_connection:
        return redirect(url_for('index', _external=True, _scheme='https'))
    else:
        return redirect(url_for('index'))

@app.route('/index.html')
def index():
    """
    Serve web interface
    """
    return app.send_static_file('index.html')

@app.route('/login', methods=['POST'])
def login():
    """
    Get an authentication session

    Sample request to authenticate:

    .. code-block:: javascript

       POST /login HTTP/1.1
       Host: janua.mydomain.com
       Content-Type: application/json

       {
         "username": "admin",
         "password": "admin",
         "language": "EN",
       }

    Sample response:

    .. code-block:: javascript

       HTTP/1.1 200

       {
         "success": true,
         "message": "Successful authentication",
         "JanuaAuthToken": "abcdef123456789",
       }

    """
    if not request.json:
        return make_response(json_error('Request format is not json'))

    if 'username' not in request.json:
        return make_response(json_error('Username is missing'))
    if 'password' not in request.json:
        return make_response(json_error('Password is missing'))
    if 'language' not in request.json:
        return make_response(json_error('Language is missing'))

    username = request.json['username']
    password = request.json['password']
    language = request.json['language']

    admin = authenticate_admin(username, password)
    if admin:
        admin_token = serialize_token(admin.id, token_serializer)
        if not admin_token:
            return make_response(json_error('Failed to generate token'))

        session_lifetime = timedelta(hours=config.web.session_lifetime)
        expire = datetime.utcnow() + session_lifetime

        response = make_response(json_success('Authentication ok', JanuaAuthToken=admin_token))

        response.set_cookie('role', get_role(admin), expires=expire)
        response.set_cookie('admin_id', str(admin.id), expires=expire)
        response.set_cookie('auth_token', admin_token, expires=expire)
        return response

    return make_response(json_error('Authentication failure'))

@app.route('/logout', methods=['GET'])
def logout():
    """
    Logout session

    Sample request to authenticate:

    .. code-block:: javascript

       GET /logout HTTP/1.1
       Host: janua.mydomain.com
       Content-Type: application/json

    Sample response:

    .. code-block:: http

       HTTP/1.1 200

    """
    if config.web.secure_connection:
        url = url_for('index', _external=True, _scheme='https')
    else:
        url = url_for('index')

    response = make_response(redirect(url))
    response.set_cookie('role', '', expires=0)
    response.set_cookie('admin_id', '', expires=0)
    response.set_cookie('auth_token', '', expires=0)

    return response
