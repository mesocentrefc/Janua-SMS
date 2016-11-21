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

import inspect
import json

from janua.commands import CommandError
from janua.db.database import Commands
import janua.utils.logger as jlogger
from janua.utils.utilities import get_subclasses

log = jlogger.getLogger(__name__)

class _code(dict):
    pass

def command(name):
    def wrap(func):
        func_args = [arg for arg in inspect.getargspec(func).args if arg != 'self']
        return _code({'code': name, 'func': func, 'args': func_args})
    return wrap

class CommandManager(object):
    _commands = {}

    def __init__(self, db):
        self.db = db

    def register(self):
        duplicate_commands = ''
        for cls in get_subclasses(DBCommand):
            commands = cls.get()
            for command, value in commands.items():
                if command in self._commands:
                    duplicate_commands += ' %s' % command
                self._commands.update({command: value})
        if duplicate_commands:
            raise CommandError('duplicate commands:%s' % duplicate_commands)

    def insert(self, command, params):
        if command not in self._commands:
            raise CommandError('Cannot insert unknown command %s' % command)
        cmd = Commands()
        cmd.command = command
        cmd.params = json.dumps(params)
        if not self.db.add_entry(cmd):
            raise CommandError('Failed to insert command %s in database' % command)

    def execute(self):
        for dbcommand in self.db.commands.get_all():
            id = dbcommand.id
            command = dbcommand.command
            params = dbcommand.params

            try:
                options = json.loads(params)
            except ValueError, err:
                self.db.del_entry(dbcommand)
                raise CommandError('params not in json format')

            if command not in self._commands:
                # unknown or not implemented commands are simply deleted and ignored
                self.db.del_entry(dbcommand)
                continue

            command_func = self._commands[command]['func']
            command_args = self._commands[command]['args']

            options_args = []
            for arg in command_args:
                if arg not in options:
                    self.db.del_entry(dbcommand)
                    raise CommandError('Command argument %s is unknown' % arg)
                else:
                    options_args.append(options[arg])

            for option in options:
                if option not in command_args:
                    self.db.del_entry(dbcommand)
                    raise CommandError('Command argument %s is missing in function %s' % (option, command_func.__name__))

            log.debug('Processing command %s' % command)
            try:
                command_func(*options_args)
            except CommandError, err:
                log.error(err)
            else:
                self.db.del_entry(dbcommand)

class _MetaDBCommand(type):
    def __new__(mcs, clsname, bases, dct):
        dct.update({'_commands_map': {}})
        for key, val in dct.items():
            if isinstance(val, _code):
                method = val
                dct['_commands_map'].update({method['code']: {'func': method['func'], 'args': method['args']}})

        return super(_MetaDBCommand, mcs).__new__(mcs, clsname, bases, dct)

class DBCommand(object):
    __metaclass__ = _MetaDBCommand

    _commands_map = {}

    @classmethod
    def get(cls):
        return cls._commands_map
