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
from janua.actions.action import Action, get_custom_action_repr
from janua.utils.utilities import get_role
from janua.ws.services import urlconfig, jsonify

class GetWebConfig(Action):
    """
    A JSON representation of available action for WEB context
    """

    category = '__INTERNAL__'

    @urlconfig('/get_web_config')
    def web(self):
        admin = jdb.admin.get_by_phone(self.phone_number)
        authorized_actions = []
        filtered = False
        if get_role(admin) == 'supervisor':
            filtered = True
            actions = jdb.action.get_by_authorized_supervisor_id(admin.id)
            authorized_actions = [action.name for action in actions]
        jsonactions = get_custom_action_repr('web', filtered, authorized_actions)
        return jsonify(**jsonactions)
