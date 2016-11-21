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

from janua.db.database import Admin
from janua.utils.utilities import hash_password
from janua.utils.pwgen import pwgen

admin_password = pwgen(pw_length=8, num_pw=1)
supervisor_passwd = pwgen(pw_length=8, num_pw=1)

admin = Admin()
admin.name = 'Test'
admin.firstname = 'Admin'
admin.phone_number = '+3312345678'
admin.password = hash_password(admin_password)
admin.email = 'admin@localhost.local'
admin.level = 1
admin.login = 'admin'

supervisor = Admin()
supervisor.firstname = 'Supervisor'
supervisor.name = 'Test'
supervisor.phone_number = '+3365478912'
supervisor.password = hash_password(supervisor_passwd)
supervisor.email = 'super@localhost.local'
supervisor.level = 2
supervisor.login = 'supervisor'