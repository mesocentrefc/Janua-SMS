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

import glob
import os
import re
import stat
import sys
import textwrap
import traceback as tb

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

quota_unit = {
    'D': 'day',
    'W': 'week',
    'M': 'month',
    'Y': 'year'
}

role_levels = ['null', 'admin', 'supervisor']

def get_role(admin):
    """
    Get admin role

    :returns: string identifying role
    """
    return role_levels[admin.level]

def get_subclasses(cls):
    """
    Get all subclasses recursively

    :param cls: parent class object
    :returns: a list of class and subclass object inheriting from cls
    """
    res = []
    for cl in cls.__subclasses__():
        res.extend(get_subclasses(cl))
        res.append(cl)
    return res

def import_available_modules(namespace, path):
    """
    Import all available module in the specified namespace.

    :param namespace: The namespace to import modules from.
    :param path: The path to namespace
    """
    fullpath = os.path.sep.join([path] + namespace.split('.'))
    pyfiles = glob.glob(os.path.sep.join([fullpath] + ['*.py']))
    modules = [pyfile.split('/')[-1] for pyfile in pyfiles]
    modules.sort()

    for module in modules:
        if module != '__init__.py':
            modpath = '.'.join([namespace, module.split('.')[0]])
            if modpath not in sys.modules:
                __import__(modpath, globals(), locals(), [''])
            else:
                reload(sys.modules[modpath])

def extract_group_number_and_mail(string):
    """
    Extract group, phone number and mail from string

    :param string: a string which can contain a mix of phone number
                   and/or group and/or mail separated by comma
    :returns: a tuple containing lists of extracted groups and numbers
    """
    parsed = {'groups': [], 'numbers': [], 'mails': []}
    phone_regex = re.compile('(\+?[0-9]+$)')
    group_regex = re.compile('([a-zA-Z0-9-]+$)')
    mail_regex = re.compile('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')

    recipient = string.split(',')

    for r in recipient:
        # match a phone number ?
        m = phone_regex.match(r)
        if m:
            parsed['numbers'].append(m.groups()[0])
            continue

        # match a role group ?
        m = group_regex.match(r)
        if m:
            parsed['groups'].append(m.groups()[0])

        # match a mail ?
        m = mail_regex.match(r)
        if m:
            parsed['mails'].append(m.groups()[0])

    return parsed['groups'], parsed['numbers'], parsed['mails']

def prompt(message):
    """
    Display message and prompt for input

    :param message: message on prompt display
    :returns: input value
    """
    sys.stdout.write('%s: ' % message)
    sys.stdout.flush()
    value = sys.stdin.readline().rstrip('\r\n')
    return value.decode('utf-8')

def valid_prefix_number(phone, prefixes=[]):
    """
    Validate phone number prefix against whitelist defined in configuration file

    :param phone: phone number
    :returns True if valid, False otherwise
    """
    if prefixes:
        for prefix in prefixes:
            if prefix != '' and phone.startswith(prefix):
                return True
        return False
    else:
        return True

def doctrim(docstring, remove_newline=True):
    """
    Dedent and strip newline for function / class documentation strings

    :param docstring: docstring to trim
    :param remove_newline: specify if newline character should be removed
    :returns: 'trimmed' docstring
    """
    return textwrap.dedent(docstring).strip('\n')

def hash_password(password):
    """
    Hash password with salt

    :param password: password to hash
    :returns: hashed password
    """
    return generate_password_hash(password, 'pbkdf2:sha256', 16)

def check_password(hash, password):
    """
    Check if password match with hashed password

    :param: hashed password
    :param: password to match against hash
    :returns: True if password math False otherwise
    """
    return check_password_hash(hash, password)
