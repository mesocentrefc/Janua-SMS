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
"""
Logger tool

To use logger in your module (action, authentication backend, sms engine),
you can declare log variable as global and use it anywhere in your code:

.. code-block:: python

   from janua.utils.logger import getLogger

   log = getLogger(__name__)

   log.debug('Module %s loaded' % __name__)

   # special case for critical log, it send a mail report to administrator
   log.critical('Something goes wrong')
"""

import sys

from werkzeug.contrib.cache import SimpleCache

from janua.utils.mail import MailObj

import logging.handlers

from logging import Handler

_MAX_BYTES = 1048576
_BACKUP_COUNT = 7
DEFAULT_FORMAT = '%(asctime)s <%(levelname)s> [%(name)s:%(lineno)d]: %(message)s'

class JanuaCriticalHandler(Handler):
    def __init__(self, email, queue):
        Handler.__init__(self)
        self.cache = SimpleCache()
        self.mailobj = MailObj()
        self.mailobj.template = 'critical_report'
        self.mailobj.to = email
        self.queue = queue

    def emit(self, record):
        # to avoid spam if its the same error notify only every hour
        log = '%s:%s' % (record.pathname, record.lineno)
        cached_log = self.cache.get(log)
        if not cached_log:
            self.cache.set(log, log, timeout=3600)
            try:
                self.mailobj.template_args = {
                    'levelname': record.levelname,
                    'pathname': record.pathname,
                    'lineno': record.lineno,
                    'module': record.module,
                    'funcName': record.funcName,
                    'asctime': record.asctime,
                    'message': record.message
                }

                self.queue.put(self.mailobj)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)

def logToOutput(logformat=DEFAULT_FORMAT):
    """
    Display debug log level on output

    :param logformat: log string format
    :returns: an output stream handler
    """
    rootlogger = logging.getLogger()
    rootlogger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(logformat)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    rootlogger.addHandler(handler)

    return handler

def logToFile(filename, logformat=DEFAULT_FORMAT, max_bytes=_MAX_BYTES, backup_count=_BACKUP_COUNT, debug=False):
    """
    Log into file

    :param filename: path to log file
    :param logformat: log string format
    :param max_bytes: max size of log file
    :param backup_count: number of log file rotation
    :param debug: set debug log level
    :returns: file log handler
    """
    rootlogger = logging.getLogger()
    if debug == True:
        rootlogger.setLevel(logging.DEBUG)
    else:
        rootlogger.setLevel(logging.INFO)
    formatter = logging.Formatter(logformat)
    handler = logging.handlers.RotatingFileHandler(filename, maxBytes=max_bytes, backupCount=backup_count)
    handler.setFormatter(formatter)
    rootlogger.addHandler(handler)

    return handler

def logToMail(email, queue):
    """
    Mail on critical log level

    :param email: email which send critical report
    :param queue: mail queue to use
    :returns: mail log handler
    """
    rootlogger = logging.getLogger()
    handler = JanuaCriticalHandler(email, queue)
    handler.setLevel(logging.CRITICAL)
    rootlogger.addHandler(handler)

    return handler

def getLogger(modulename=''):
    """
    Get module logger

    :param modulename: module name
    :returns: logger corresponding to module
    """
    logger = logging.getLogger(modulename)
    return logger
