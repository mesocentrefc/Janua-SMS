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

from janua import jdb

def get_contact_ids(admin):
    return [contact.id for contact in jdb.contact.get_by_admin_phone(admin.phone_number)]

def get_action_ids(admin):
    return [action.id for action in jdb.action.get_all()
            if action.admin_id == admin.id]

def get_group_ids(admin):
    return [group.id for group in jdb.group.get_by_admin_phone(admin.phone_number)]

def get_authorized_group_ids(admin):
    return [authorized_group.id for authorized_group in jdb.authorized_group.get_by_admin_id(admin.id)]

def get_contact_group_ids(admin):
    group_ids = get_group_ids(admin)
    return [contact_group.id for contact_group in jdb.contact_group.get_by_group_id(group_ids)]

def get_action_contact_ids(action_id):
    return [contact.id for contact in jdb.contact.get_by_action_id(action_id)]

def get_contact_notify_ids(admin):
    return [contact_notify.id for contact_notify in jdb.contact_notify.get_by_admin_id(admin.id)]

def get_action_group_ids(admin):
    return [authorized_group.group_id for authorized_group in jdb.authorized_group.get_by_admin_id(admin.id)]
