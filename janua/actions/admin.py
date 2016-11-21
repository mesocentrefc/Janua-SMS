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

import getpass
import sys

from janua import jdb, config
from janua.actions.action import Action, argument
from janua.actions.action import console_error, console_success
from janua.utils.pwgen import pwgen
from janua.utils.mail import valid_email
from janua.utils.utilities import prompt, hash_password, get_role
from janua.utils.utilities import valid_prefix_number

class Admin(Action):
    """
    Manage administrator
    """

    category = '__INTERNAL__'

    def add_admin(self):
        level = 2
        levelname = 'supervisor'

        print 'Check database for a super admin entry:',
        if jdb.admin.has_super_admin():
            print 'Found'
        else:
            print 'Not found'
            level = 1
            levelname = 'admin'

        login = prompt('Enter %s login' % levelname)
        if login == '':
            return console_success('exit')

        firstname = prompt('Enter %s firstname' % levelname)
        if firstname == '':
            return console_success('exit')

        name = prompt('Enter %s name' % levelname)
        if name == '':
            return console_success('exit')

        while True:
            phone_number = prompt(
                'Enter %s phone number in international '
                'form (eg: +33123456789)' % levelname
            )
            if phone_number == '':
                return console_success('exit')
            if not valid_prefix_number(phone_number, config.sms.prefix_filter):
                print('phone number prefix not allowed')
            else:
                break

        while True:
            mail = prompt('Enter %s email' % levelname)
            if mail == '':
                return console_success('exit')
            if not valid_email(mail):
                print('%s is not a valid email address, '
                      'please enter a valid one' % mail)
            else:
                break

        generate_password = False
        while True:
            password = getpass.getpass('Enter a password (if empty, a '
                                       'password will be generated): ')
            if password == '':
                generate_password = True
                break
            else:
                repassword = getpass.getpass('Re-enter password: ')
                if password != repassword:
                    print 'Passwords entered don\'t match'
                else:
                    break

        if generate_password:
            password = pwgen(
                pw_length=8,
                capitalize=True,
                no_symbols=True,
                no_ambiguous=True
            )
            print '%s password is %s' % (levelname.title(), password)

        if level == 1:
            password = hash_password(password)

        if jdb.admin.add(firstname, name, phone_number,
                               password, mail, level, login):
            return console_success('%s was added' % levelname.title())
        else:
            return console_error('%s wasn\'t added, an error occured'
                              % levelname.title())

    def del_admin(self):
        admins = jdb.admin.get_all()
        if len(admins) == 1:
            return console_success('No supervisor in database')

        print 'Select an admin to delete:'
        idx = 0
        for admin in admins:
            if get_role(admin) == 'supervisor':
                print '%d. %s %s' % (idx, admin.firstname, admin.name)
            idx += 1
        admin_id = prompt('Enter a number (or ENTER to quit)')
        if admin_id.isdigit():
            response = prompt('Are you sure ? (type \'yes\')')
            if response == 'yes':
                admin_id = int(admin_id)
                admin = admins[admin_id]
                entry = '%s %s' % (admin.firstname, admin.name)
                if jdb.del_entry(admin) == False:
                    return console_error('failed to delete entry %s' % entry)
                else:
                    return console_success('entry %s has been deleted' % entry)
            else:
                return console_success('operation has been canceled')
        else:
            return console_success('operation has been canceled')

    def console(self):
        operation = self.operation()
        if operation == 'add':
            print('Add an administrator entry in database '
                  '(or ENTER to quit)')
            return self.add_admin()
        elif operation == 'delete':
            print('[WARNING] Delete an admin entry will delete all entries ' \
                  'associated to, including groups and contacts')
            return self.del_admin()
        else:
            return console_error('operation %s not supported' % operation)

    @argument(required=True)
    def operation(self):
        """Operation: add, delete"""
        return ['add', 'delete']
