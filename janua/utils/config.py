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

import os
import stat

from configobj import ConfigObj, flatten_errors, ConfigspecError
from validate import Validator

class JanuaConfigError(Exception):
    pass

configspec = """#
# General section
#
[janua]
log_file = string(default='/var/log/janua/janua.log')    ; where to stock log file
pid_file = string(default='/var/run/janua.pid')    ; where to stock pid file
user = string(default='nobody')    ; run as user
group = string(default='nogroup')    ; run as group

#
# web server section
#
[web]
bind_address = string(min=7, max=15, default='127.0.0.1')    ; bind web server on address
hostname = string(min=1, default='localhost')     ; web hostname
port = integer(1, 65535, default=5000)    ; run web server on port
url = string(default=None)
session_lifetime = integer(1, 24, default=12)     ; web session lifetime in hour
secure_connection = boolean(default=False)      ; use ssl connection ?
ssl_certificate = string(default=None)     ; path to ssl certificate
ssl_private_key = string(default=None)     ; path to ssl private key
log_requests = boolean(default=True)       ; log all requests ?

#
# sms interface section
#
[sms]
engine = string(default='serial')    ; sms engine to use
phone_number = string(max=25, default='5554')    ; phone number used by the server in international form
pin_code = string(default='0000')    ; pin code number
send_interval = integer(default=5)     ; time to wait before sending message
prefix_filter = force_list(default=list())   ; whitelist prefix list sperated by commas, only phone numbers which start with these prefixes are allowed

#
# mailer section
# don't support authentication, you have to setup a smtp relay server
#
[mail]
enable = boolean(default=True)
smtp_host = string(default=None)    ; smtp relay hostname
smtp_port = integer(1, 65535, default=25)    ; smtp relay port
smtp_username = string(default=None)
smtp_password = string(default=None)
smtp_ssl = boolean(default=True)
smtp_tls = boolean(default=False)
smtp_timeout = integer(default=10)
mail_from = string(default=None)    ; mail are originated from
mail_language = option('EN', 'FR', default='EN')"""

class Config(object):
    """
    Janua configuration class setup
    """
    def __init__(self, config_file, config_spec=None):
        """
        Initialize configuration class

        :param configfile: path to configuration file
        :param configspec: path to configuration specification, or a string
        """
        self.configfile = config_file
        self.configspec = config_spec

    def create(self):
        """
        Create default configuration file if it doesn't exists
        """
        if self.configspec and self.configfile:
            if not os.path.exists(self.configfile):
                confdir = os.path.dirname(self.configfile)
                if not os.path.exists(confdir):
                    os.makedirs(confdir)
                config = ConfigObj(configspec=self.configspec.split('\n'), encoding='UTF8', interpolation=False, list_values=False)
                config.stringify = False
                config.write_empty_values = True
                config.filename = self.configfile
                validation = Validator()
                config.validate(validation, preserve_errors=True, copy=True)
                config.write()
                os.chmod(self.configfile, stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP)

    def parse(self):
        """
        Parse configuration file and validate it if a configuration specification was supplied
        """
        if self.configspec and self.configfile:
            cfgspec = ConfigObj(self.configspec.split('\n'), encoding='UTF8', interpolation=False, list_values=False)
            conf = ConfigObj(self.configfile, configspec=cfgspec)
            validation = Validator()
            res = conf.validate(validation, preserve_errors=True)

            for entry in flatten_errors(conf, res):
                # each entry is a tuple
                section_list, key, error = entry
                if key is not None:
                    section_list.append(key)
                else:
                    section_list.append('[missing section]')
                if error == False:
                    error = 'Missing value or section.'
                raise JanuaConfigError('%s parameter in section %s: %s' % (section_list[1], section_list[0], error))

            return DictToObj(conf)

class DictToObj(object):
    """
    Convert a dictionary to a simple object
    """
    def __init__(self, adict):
        """
        Initialization

        :param adict: dictionary to convert
        """
        self.__dict__.update(adict)
        for k, v in adict.iteritems():
            if isinstance(v, dict):
                self.__dict__[k] = DictToObj(v)
