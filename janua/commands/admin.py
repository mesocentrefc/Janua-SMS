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

from janua import jdb, mail_queue
from janua.commands import CommandError
from janua.commands.db import command, DBCommand
from janua.utils.mail import MailObj, MailError
from janua.utils.utilities import quota_unit, hash_password
from janua.ws.services import get_url
from janua.ws.auth import auth_manager

class AdminCommands(DBCommand):
    @command('ADD_ADMIN')
    def add_admin(login, email, phone_number, password, auth_backend):
        url = get_url()
        backend = auth_manager.get(auth_backend)

        admin = jdb.admin.get_by_login(login)
        if not admin:
            raise CommandError('Can\'t retrieve supervisor %s' % login)
        admin.password = hash_password(password)
        if not jdb.update_entry(admin):
            raise CommandError('Can\'t update %s password' % login)

        if not backend:
            raise CommandError('There is no %s backend' % auth_backend)

        template = backend.mail_template_creation
        template_args = {
            'phone_number': phone_number,
            'password': password,
            'url': url
        }
        sadmin = jdb.admin.get_super_admin()
        if not sadmin:
            raise CommandError('There is no super admin in database')
        try:
            mailobj = MailObj()
            mailobj.template = template
            mailobj.template_args = template_args
            mailobj.to = email
            mailobj.reply_to = sadmin.email
            mailobj.bcc = [sadmin.email]
        except MailError, err:
            raise CommandError(err)

        mail_queue.put(mailobj)

    @command('DELETE_ADMIN')
    def delete_admin(email):
        sadmin = jdb.admin.get_super_admin()
        if not sadmin:
            raise CommandError('There is no super admin in database')
        template = 'delete_admin'
        try:
            mailobj = MailObj()
            mailobj.template = template
            mailobj.template_args = {}
            mailobj.to = email
            mailobj.reply_to = sadmin.email
            mailobj.bcc = [sadmin.email]
        except MailError, err:
            raise CommandError(err)

        mail_queue.put(mailobj)

    @command('UPDATE_QUOTA')
    def update_quota(quota, email):
        limit, unit = quota.split(' ')
        sadmin = jdb.admin.get_super_admin()
        if not sadmin:
            raise CommandError('There is no super admin in database')

        template = 'update_quota'
        template_args = {
            'limit': limit,
            'unit': quota_unit[unit],
        }
        try:
            mailobj = MailObj()
            mailobj.template = template
            mailobj.template_args = template_args
            mailobj.to = email
            mailobj.reply_to = sadmin.email
            mailobj.bcc = [sadmin.email]
        except MailError, err:
            raise CommandError(err)

        mail_queue.put(mailobj)

    @command('REQUEST_QUOTA')
    def request_quota(old_quota, new_quota, name):
        new_limit, new_unit = new_quota[1:].split(' ')
        current_limit, current_unit = old_quota.split(' ')

        sadmin = jdb.admin.get_super_admin()
        if not sadmin:
            raise CommandError('There is no super admin in database')

        template = 'request_quota'
        template_args = {
            'current_limit': current_limit,
            'current_unit': quota_unit[current_unit],
            'new_limit': new_limit,
            'new_unit': quota_unit[new_unit],
            'name': name
        }
        try:
            mailobj = MailObj()
            mailobj.template = template
            mailobj.template_args = template_args
            mailobj.to = sadmin.email
            mailobj.bcc = [sadmin.email]
        except MailError, err:
            raise CommandError(err)

        mail_queue.put(mailobj)
