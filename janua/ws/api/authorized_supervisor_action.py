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
==================================  ==============================  ==========================
Location                            Methods                         Authorized roles
==================================  ==============================  ==========================
/api/AUTHORIZED_SUPERVISOR_ACTION   GET, POST, DELETE               admin
==================================  ==============================  ==========================
"""

from flask_restless import ProcessingException

from janua.ws.api.base import BaseApi
from janua.ws.auth import get_role

from janua.db.database import AuthorizedSupervisorAction as AuthorizedSupervisorActionTable

class AuthorizedSupervisorAction(BaseApi):
    """
    Authorized supervisor action REST API
    
    Expose database object: :class:`AuthorizedSupervisorAction <janua.db.database.AuthorizedSupervisorAction>`
    """
    methods = ['GET', 'POST', 'DELETE']
    model = AuthorizedSupervisorActionTable
