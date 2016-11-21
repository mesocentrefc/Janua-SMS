# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# Copyright (C) 2004 Paul Hardwick <paul@peck.org.uk>
# Copyright (C) 2008 Warp Networks S.L.
# Copyright (C) 2008 Telefonica I+D
# Copyright (C) 2008 Francois Aucamp <francois.aucamp@gmail.com>
#
# Imported for the wader project on 5 June 2008 by Pablo Martí
# Imported for the mobile-manager on 1 Oct 2008 by Roberto Majadas
#
# Copyright (C) 2008-2010 python-messaging developers
#
# http://github.com/pmarti/python-messaging
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

SEVENBIT_SIZE = 160
EIGHTBIT_SIZE = 140
UCS2_SIZE = 70
SEVENBIT_MP_SIZE = SEVENBIT_SIZE - 7
EIGHTBIT_MP_SIZE = EIGHTBIT_SIZE - 6
UCS2_MP_SIZE = UCS2_SIZE - 3

# address type
UNKNOWN = 0
INTERNATIONAL = 1
NATIONAL = 2
NETWORK_SPECIFIC = 3
SUBSCRIBER = 4
ALPHANUMERIC = 5
ABBREVIATED = 6
RESERVED = 7
