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

import json
import time
import Queue

import janua.utils.logger as jlogger

from janua.activity.activity import Activity
from janua import jdb

from janua.commands.db import CommandManager
from janua.commands import CommandError
from janua.commands.admin import AdminCommands

log = jlogger.getLogger(__name__)

class ProcessCommandActivity(Activity):
    """
    A background process activity for database commands
    """
    def __init__(self, *args, **kwargs):
        super(ProcessCommandActivity, self).__init__(*args, **kwargs)
        self.cmd_manager = CommandManager(jdb)
        try:
            self.cmd_manager.register()
        except CommandError, err:
            log.error(err)

    def run(self):
        while not self._stopevent.isSet():
            try:
                command, params = self.queue.get(True, 1)
            except Queue.Empty:
                pass
            else:
                try:
                    self.cmd_manager.insert(command, params)
                except CommandError, err:
                    log.error(err)
            try:
                self.cmd_manager.execute()
            except CommandError, err:
                log.error(err)
