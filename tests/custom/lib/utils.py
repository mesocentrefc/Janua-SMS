# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# Copyright (c) 2014 Cédric Clerget
# Copyright (c) 2016 HPC Center - Franche-Comté University
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

from janua.actions.action import get_custom_action_repr

def get_arg_id_for_action_param(action, param):
    action = get_custom_action_repr('sms', True, authorized_actions=[action])['action'][0]
    arg_id = -1
    for arg in action['args']:
        if arg['name'] == param:
            arg_id = arg['id']
            break
    return arg_id