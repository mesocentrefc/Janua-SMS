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
import sys
import platform

januapath = os.environ['JANUAPATH']

arch = platform.architecture()[0]

SL4A_PATH = os.path.join(januapath, 'packages', 'sl4a_r6.apk')

if arch == '64bit':
    package = 'platform-tools_r24.0.3-linux.zip'
else:
    package = 'platform-tools_r19.0.1-linux.zip'

PLATFORM_TOOLS_PATH = os.path.join(januapath, 'packages', package)

LOCALHOST = 'localhost'
SL4A_SERVER_PORT = SL4A_HOST_PORT = 45001
ADB_PORT = 5037
ADB_PATH = os.path.join(januapath, 'bin', 'adb')
