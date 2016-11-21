# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# This code snippet has been taken from: http://flask.pocoo.org/snippets/88
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
import sqlite3
from cPickle import loads, dumps
from Queue import Queue
from time import sleep
try:
    from thread import get_ident
except ImportError:
    from dummy_thread import get_ident

class SqliteQueue(object):

    _create = (
            'CREATE TABLE IF NOT EXISTS queue ' 
            '('
            '  id INTEGER PRIMARY KEY AUTOINCREMENT,'
            '  item BLOB'
            ')'
            )
    _count = 'SELECT COUNT(*) FROM queue'
    _iterate = 'SELECT id, item FROM queue'
    _append = 'INSERT INTO queue (item) VALUES (?)'
    _write_lock = 'BEGIN IMMEDIATE'
    _popleft_get = (
            'SELECT id, item FROM queue '
            'ORDER BY id LIMIT 1'
            )
    _popleft_del = 'DELETE FROM queue WHERE id = ?'
    _peek = (
            'SELECT item FROM queue '
            'ORDER BY id LIMIT 1'
            )

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self._connection_cache = {}
        with self._get_conn() as conn:
            conn.execute(self._create)

    def __len__(self):
        with self._get_conn() as conn:
            l = conn.execute(self._count).next()[0]
        return l

    def __iter__(self):
        with self._get_conn() as conn:
            for id, obj_buffer in conn.execute(self._iterate):
                yield loads(str(obj_buffer))

    def _get_conn(self):
        id = get_ident()
        if id not in self._connection_cache:
            self._connection_cache[id] = sqlite3.Connection(self.path, 
                    timeout=60)
        return self._connection_cache[id]

    def append(self, obj):
        obj_buffer = buffer(dumps(obj, 2))
        with self._get_conn() as conn:
            conn.execute(self._append, (obj_buffer,)) 

    def popleft(self, sleep_wait=True):
        keep_pooling = True
        wait = 0.1
        max_wait = 2
        tries = 0
        with self._get_conn() as conn:
            id = None
            while keep_pooling:
                conn.execute(self._write_lock)
                cursor = conn.execute(self._popleft_get)
                try:
                    id, obj_buffer = cursor.next()
                    keep_pooling = False
                except StopIteration:
                    conn.commit() # unlock the database
                    if not sleep_wait:
                        keep_pooling = False
                        continue
                    tries += 1
                    sleep(wait)
                    wait = min(max_wait, tries/10 + wait)
            if id:
                conn.execute(self._popleft_del, (id,))
                return loads(str(obj_buffer))
        return None

    def peek(self):
        with self._get_conn() as conn:
            cursor = conn.execute(self._peek)
            try:
                return loads(str(cursor.next()[0]))
            except StopIteration:
                return None

class PersistentSqliteQueue(Queue):
    """
    A persistent sqlite queue
    """

    def __init__(self, path, *args, **kwargs):
        """
        Initialize the persistent queue

        :param path: path to sqlite database file
        """
        self.path = path
        Queue.__init__(self, *args, **kwargs)

    def _init(self, maxsize):
        self.queue = SqliteQueue(self.path)

    def _qsize(self, len=len):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.popleft()
