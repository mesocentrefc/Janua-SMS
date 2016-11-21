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

from janua.actions.action import Action, argument
from janua.actions.action import console_error, console_success
from janua.actions.action import date, time, multilist
from janua.ws.services import urlconfig, jsonify

class Test(Action):
    """
    Test action
    """
    category = 'TEST'

    def console(self):
        if (self.str_param() == 'error'):
            return console_error('Error')
        elif (self.str_param() == 'success'):
            return console_success('Success')
        else:
            return console_error('Fail')

    def sms(self):
        self.notify.sms.sender(self.str_param())

    @urlconfig('/test')
    def web(self):
        return jsonify(success=True)

    @argument(required=False)
    def str_param(self):
        """Test string param"""
        return ""
    
    @argument(required=False)
    def int_param(self):
        """Test int param"""
        return int()
    
    @argument(required=False)
    def list_param(self):
        """Test list param"""
        return ['test']

    @argument(required=False)
    def date_param(self):
        """Test date param"""
        return date()
    
    @argument(required=False)
    def time_param(self):
        """Test time param"""
        return time()
    
    @argument(required=False)
    def float_param(self):
        """Test float param"""
        return float()

    @argument(required=False)
    def multilist_param(self):
        """Test multilist param"""
        return multilist(['TEST1', 'TEST2', 'TEST3'])