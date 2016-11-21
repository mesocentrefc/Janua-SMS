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

import cherrypy

import janua.utils.logger as jlogger

from janua import config
from janua.activity.activity import Activity

from paste.translogger import TransLogger

log = jlogger.getLogger(__name__)

class WebActivity(Activity):
    """
    Web thread activity. Its the main thread of Janua, that's why run and join
    methods does nothing, and start is overriden as a simple function called from main.
    """
    def __init__(self, app, *args, **kwargs):
        super(WebActivity, self).__init__(*args, **kwargs)
        if config.web.log_requests:
            msg_format = ('%(REQUEST_METHOD)s %(status)s %(REQUEST_URI)s (%(REMOTE_ADDR)s) %(bytes)s')
            app_logged = TransLogger(app, logger=log, format=msg_format)
            cherrypy.tree.graft(app_logged, '/')
        else:
            cherrypy.log.error_log.propagate = False
            cherrypy.log.access_log.propagate = False
            cherrypy.tree.graft(app)

        cherrypy.config.update({
            'engine.autoreload.on': False,
            'log.screen': False,
            'server.socket_port': config.web.port,
            'server.socket_host': config.web.bind_address
        })
        if config.web.ssl_certificate and config.web.ssl_private_key:
            cherrypy.config.update({
                'server.ssl_module': 'builtin',
                'server.ssl_certificate': config.web.ssl_certificate,
                'server.ssl_private_key': config.web.ssl_private_key
            })

    def start(self):
        cherrypy.engine.start()
        cherrypy.engine.block()

    def join(self):
        pass

    def stop(self):
        cherrypy.engine.exit()
        cherrypy.server.stop()
