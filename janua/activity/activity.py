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

import threading
import Queue

import janua.utils.logger as jlogger

log = jlogger.getLogger(__name__)

class ActivityManager(object):
    def __init__(self):
        self._pool_activity = []

    def register(self, activity):
        self._pool_activity.append(activity)

    def start(self):
        """Start all threads activities"""
        for activity in self._pool_activity:
            log.debug('Starting %s thread' % activity.name)
            activity.start()

    def join(self):
        """Wait all threads activities to terminate"""
        for activity in reversed(self._pool_activity):
            log.debug('Waiting %s thread' % activity.name)
            activity.join()

    def stop(self, signum, stack):
        """Signal handler to stop all threads activities"""
        for activity in reversed(self._pool_activity):
            log.debug('Stopping %s thread' % activity.name)
            activity.stop()

class Activity(threading.Thread):
    """Class registering a thread activity"""
    def __init__(self, *args, **kwargs):
        super(Activity, self).__init__(*args, **kwargs)
        self.queue = Queue.Queue()
        self._stopevent = threading.Event()
        self.name = self.__class__.__name__

    def run(self):
        """Thread activity"""
        pass

    def stop(self):
        """Stop activity"""
        self._stopevent.set()
