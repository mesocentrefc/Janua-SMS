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

import grp
import os
import pwd
import sys
import stat

if os.environ['JANUAPATH']:
    januapath = os.environ['JANUAPATH']
else:
    januapath = '/opt/janua'
    os.environ['JANUAPATH'] = '/opt/janua'

from janua.utils.config import Config, configspec
from janua.utils import exit_error
from janua.utils.utilities import import_available_modules, get_subclasses
from janua.sms.engine import SMSEngine
from janua.sms.android import AndroidSMS
from janua.sms.serialmodem import SerialSMS
from janua.db.connection import JanuaDB
from janua.utils.sqlite_queue import PersistentSqliteQueue

conf_dir = os.path.join(januapath, 'conf')
bin_dir = os.path.join(januapath, 'bin')
custom_dir = os.path.join(januapath, 'custom')

if not os.path.exists(conf_dir):
    os.makedirs(conf_dir)
if not os.path.exists(bin_dir):
    os.makedirs(bin_dir)

if januapath not in sys.path:
    sys.path.append(januapath)

os.environ['PATH'] = ':'.join([os.environ['PATH'], os.path.join(januapath, 'bin')])

try:
    import_available_modules('custom.engine', januapath)
except Exception, err:
    exit_error('Failed to import custom SMS engine: %s', err)

sms_engines = {}
cfg_spec = configspec

for sms_engine in get_subclasses(SMSEngine):
    if sms_engine.config_spec.startswith('\n'):
        cfg_spec += sms_engine.config_spec
    else:
        cfg_spec += '\n%s' % sms_engine.config_spec
    sms_engines.update({sms_engine.name: sms_engine})

cfg = Config(os.path.join(januapath, 'conf', 'server.cfg'), config_spec=cfg_spec)

try:
    cfg.create()
except Exception, err:
    exit_error('Failed to create configuration file: %s' % err)

try:
    config = cfg.parse()
except Exception, err:
    exit_error('Failed to parse configuration file: %s' % err)

try:
    uid = pwd.getpwnam(config.janua.user).pw_uid
    if (uid != 0 and uid != os.getuid()):
        uid = os.getuid()
except KeyError:
    exit_error('User %s not found on system' %  config.janua.user)

try:
    gid = grp.getgrnam(config.janua.group).gr_gid
    if (gid != 0 and gid != os.getgid()):
        gid = os.getgid()
except KeyError:
    exit_error('Group %s not found on system' %  config.janua.group)

os.chown(conf_dir, uid, gid)
os.chmod(conf_dir, stat.S_IRWXU)
os.chown(bin_dir, uid, gid)
os.chmod(bin_dir, stat.S_IRWXU)
os.chown(custom_dir, uid, gid)
os.chmod(custom_dir, stat.S_IRWXU)

januadb = os.path.join(conf_dir, 'janua.db')
jdb = JanuaDB(januadb)
os.chown(januadb, uid, gid)
os.chmod(januadb, stat.S_IRUSR | stat.S_IWUSR)

maildb = os.path.join(conf_dir, 'mailqueue.db')
mail_queue = PersistentSqliteQueue(maildb)
os.chown(maildb, uid, gid)
os.chmod(maildb, stat.S_IRUSR | stat.S_IWUSR)

smsdb = os.path.join(conf_dir, 'smsqueue.db')
sms_queue = PersistentSqliteQueue(smsdb)
os.chown(smsdb, uid, gid)
os.chmod(smsdb, stat.S_IRUSR | stat.S_IWUSR)
