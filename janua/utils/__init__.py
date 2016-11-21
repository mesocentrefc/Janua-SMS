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

import traceback as tb
import sys

def exit_error(error_msg, traceback=False):
    """
    Print an error with traceback on standard error output and exit

    @param error_msg: error message to display
    """
    sys.stderr.write('\033[1m\033[31m[ERROR]\033[0m\033[0;0m %s\n' % error_msg)
    if traceback:
        tb.print_exc()
    sys.exit(1)

def exit_info(info_msg):
    """
    Print info on standard output and exit

    @param info_msg: information message to display
    """
    sys.stderr.write('\033[1m\033[93m[INFO]\033[0m\033[0;0m %s\n' % info_msg)
    sys.exit(0)
