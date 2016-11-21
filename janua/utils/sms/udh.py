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

class PortAddress(object):

    def __init__(self, dest_port, orig_port, eight_bits):
        self.dest_port = dest_port
        self.orig_port = orig_port
        self.eight_bits = eight_bits

    def __repr__(self):
        args = (self.dest_port, self.orig_port)
        return "<PortAddress dest_port: %d orig_port: %d>" % args


class ConcatReference(object):

    def __init__(self, ref, cnt, seq, eight_bits):
        self.ref = ref
        self.cnt = cnt
        self.seq = seq
        self.eight_bits = eight_bits

    def __repr__(self):
        args = (self.ref, self.cnt, self.seq)
        return "<ConcatReference ref: %d cnt: %d seq: %d>" % args


class UserDataHeader(object):

    def __init__(self):
        self.concat = None
        self.ports = None
        self.headers = {}

    def __repr__(self):
        args = (self.headers, self.concat, self.ports)
        return "<UserDataHeader data: %s concat: %s ports: %s>" % args

    @classmethod
    def from_status_report_ref(cls, ref):
        udh = cls()
        udh.concat = ConcatReference(ref, 0, 0, True)
        return udh

    @classmethod
    def from_bytes(cls, data):
        udh = cls()
        while len(data):
            iei = data.pop(0)
            ie_len = data.pop(0)
            ie_data = data[:ie_len]
            data = data[ie_len:]
            udh.headers[iei] = ie_data

            if iei == 0x00:
                # process SM concatenation 8bit ref.
                ref, cnt, seq = ie_data
                udh.concat = ConcatReference(ref, cnt, seq, True)

            if iei == 0x08:
                # process SM concatenation 16bit ref.
                ref = ie_data[0] << 8 | ie_data[1]
                cnt = ie_data[2]
                seq = ie_data[3]
                udh.concat = ConcatReference(ref, cnt, seq, False)

            elif iei == 0x04:
                # process App port addressing 8bit
                dest_port, orig_port = ie_data
                udh.ports = PortAddress(dest_port, orig_port, False)

            elif iei == 0x05:
                # process App port addressing 16bit
                dest_port = ie_data[0] << 8 | ie_data[1]
                orig_port = ie_data[2] << 8 | ie_data[3]
                udh.ports = PortAddress(dest_port, orig_port, False)

        return udh
