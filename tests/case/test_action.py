#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# Copyright (c) 2016 Cédric Clerget - HPC Center of Franche-Comté University
#
# This file is part of Janua
#
# http://github.com/mesocentrefc/Janua
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

import unittest

from janua.actions import ActionError
from janua.actions.action import available_action_dict, available_action_list
from janua.actions.action import time, date, multilist
from janua.ws.services import get_url
from custom.actions.test import Test
from custom.lib.consts import admin, supervisor
from custom.lib.utils import get_arg_id_for_action_param
from janua import jdb

class TestAction(unittest.TestCase):
    def __init__(self, name, sms=None, admin_password=None):
        super(TestAction, self).__init__(name)
        self.sms = sms

    def test_console_context_error(self):
        action = Test()
        success, message = action.call_console_context({'str_param': ['error']})
        self.assertTupleEqual((success, message), (False, 'Error'))

    def test_console_context_success(self):
        action = Test()
        success, message = action.call_console_context({'str_param': ['success']})
        self.assertTupleEqual((success, message), (True, 'Success'))

    def test_console_context_fail(self):
        action = Test()
        success, message = action.call_console_context({'str_param': 'success'})
        self.assertTupleEqual((success, message), (False, 'Fail'))
    
    def test_sms_context_params(self):
        action = Test()
        args = [
            ('str_param', 'hello', 'hello'),
            ('int_param', '10', 10),
            ('float_param', '1.0', 1.0),
            ('time_param', '1324569870', 1324569870),
            ('date_param', '2016/01/01', '2016/01/01'),
            ('list_param', '0', 'test'),
            ('multilist_param', '0,2', ['TEST1', 'TEST3'])
        ]
        arguments = []
        for arg in args:
            arg_id = get_arg_id_for_action_param('test', arg[0])
            self.assertNotEqual(arg_id, -1)
            arguments.append([str(arg_id), arg[1]])

        action.call_sms_context(arguments, False)
        for arg in args:
            meth = getattr(action, arg[0])
            self.assertEqual(meth(), arg[2])

    def test_zero_config(self):
        self.sms.fake_receive('test:0', admin.phone_number)
        message = self.sms.get_send_messages()
        print message
        self.assertListEqual(message, [('1:%s' % (get_url() + 'get_sms_config'), admin.phone_number)])

    def test_bad_sender_zero_config(self):
        self.sms.fake_receive('test:0', supervisor.phone_number)
        message = self.sms.get_send_messages()
        self.assertListEqual(message, [])

    def test_sms_context_test_action(self):
        jid = Test.get_id()
        dbadmin = jdb.admin.get_super_admin()
        dbadmin.phone_token = 'abcdefgh'
        jdb.update_entry(dbadmin)
        arg_id = get_arg_id_for_action_param('test', 'str_param')
        self.assertNotEqual(arg_id, -1)
        self.sms.fake_receive('%s:%d:%d,hello' % (dbadmin.phone_token, jid, arg_id), admin.phone_number)
        message = self.sms.get_send_messages()
        self.assertListEqual(message, [('hello', admin.phone_number)])