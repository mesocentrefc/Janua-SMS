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

import gc
import grp
import os
import pwd
import signal
import sys

import janua.utils.logger as jlogger

from janua import uid, gid
from janua.ws.services import app

import janua.actions as janua_action_package
import janua.actions.action as janua_action

from janua.actions.action import available_action_list, available_action_dict
from janua.actions.action import Action, update_action_table
from janua.actions import ActionError, ActionNotifyError
from janua.activity.activity import ActivityManager
from janua.activity.process_command import ProcessCommandActivity
from janua.activity.process_sms import ProcessSmsActivity
from janua.activity.receive_sms import ReceiveSmsActivity
from janua.activity.send_sms import SendSmsActivity
from janua.activity.send_mail import SendMailActivity
from janua.activity.web import WebActivity
from janua.sms import SMSError, ModemError
from janua.utils.args import ArgParse
from janua.utils.daemon import Daemon
from janua.utils.version import VERSION
from janua.utils import exit_error, exit_info
from janua.utils.utilities import import_available_modules, get_subclasses
from janua import jdb, sms_engines, config, mail_queue, januapath

try:
    # don't modify order of these imports
    from janua.actions import get_config
    from janua.actions import sendsms
    from janua.actions import admin
    from janua.actions import log
    from janua.actions import maintenance
    from janua.actions import sendmail
    from janua.actions import get_sms_config
    from janua.actions import get_web_config
    from janua.actions import get_auth_backend
    from janua.actions import set_auth_backend
    from janua.actions import list_auth_backend
    from janua.actions import sms_stats
    from janua.actions import sms_usage
except Exception, err:
    exit_error('Failed to import internal actions', traceback=True)

try:
    import_available_modules('custom.actions', januapath)
except Exception, err:
    exit_error('Failed to import custom actions', traceback=True)

log = jlogger.getLogger(__name__)

def reload_janua(signum, stack):
    internal_actions = [action for action in get_subclasses(Action)
                                   if 'janua.actions' in action.__module__]
    log.info('Reload custom actions')
    try:
        reload(janua_action)
        janua_action.action_ref['id'] = len(internal_actions)
    except Exception, err:
        log.error('Failed to reload action: %s', err)
        return
    try:
        import_available_modules('custom.actions', januapath)
    except Exception, err:
        log.error('Failed to reload custom actions: %s', err)
        return

    update_action_table()

    try:
        import_available_modules('custom.auth', januapath)
    except Exception, err:
        log.error('Failed to reload custom authentication backends: %s', err)

    gc.collect()

def exit_no_super_admin():
    exit_error('Please create a super administrator first by running: '
               '%s action admin --operation add' % sys.argv[0])

def start(debug=False, dev=False, test_activity=None):
    app.debug = debug

    if dev and not test_activity:
        handler = jlogger.logToOutput()
        app.logger.addHandler(handler)
    elif not dev and not test_activity:
        handler = jlogger.logToFile(config.janua.log_file, debug=debug)
        app.logger.addHandler(handler)

    super_admin = jdb.admin.get_super_admin()

    if not super_admin:
        exit_no_super_admin()
    else:
        update_action_table()

    activity = ActivityManager()

    signal.signal(signal.SIGINT, activity.stop)
    signal.signal(signal.SIGTERM, activity.stop)
    signal.signal(signal.SIGHUP, reload_janua)

    if config.sms.engine not in sms_engines:
        exit_error(
            'SMS engine %s not available, possible values: %s' %
            (
                config.sms.engine,
                ', '.join('"' + se + '"' for se in sms_engines.iterkeys())
            )
        )

    log.info('Server started')

    try:
        sms = sms_engines[config.sms.engine](config)
    except (SMSError, ModemError), msg:
        exit_error('Server stopped due to error: %s' % msg)

    if not test_activity:
        send_mail = SendMailActivity(config.mail)
    send_sms = SendSmsActivity(sms)
    process_command = ProcessCommandActivity()
    process_sms = ProcessSmsActivity(sms)
    receive_sms = ReceiveSmsActivity(sms, process_sms.queue)

    if not dev:
        jlogger.logToMail(super_admin.email, mail_queue)

    web = WebActivity(app)

    activity.register(process_sms)
    activity.register(receive_sms)
    activity.register(send_sms)
    if not test_activity:
        activity.register(send_mail)
    activity.register(process_command)

    if test_activity:
        test_process = test_activity(activity, sms)
        activity.register(test_process)

    # The last thread is the main thread, for Janua its the web server
    activity.register(web)
    
    # Starting threads
    activity.start()

    # Waiting threads to finish
    activity.join()

    log.info('Server exited')

    if test_activity and test_process.quit:
        test_process.quit()

def daemonize():
    return Daemon(config.janua.pid_file, logfile=config.janua.log_file,
                  uid=uid, gid=gid)

def run_server(debug=False):
    daemon = daemonize()
    daemon.run = start
    daemon.start(debug=debug)

def start_command(args):
    run_server()

def debug_command(args):
    run_server(debug=True)

def dev_command(args):
    start(debug=True, dev=True)

def stop_command(args):
    daemon = daemonize()
    daemon.stop()

def restart_command(args):
    daemon = daemonize()
    daemon.run = start
    daemon.stop()
    daemon.start(debug=False)

def status_command(args):
    daemon = daemonize()
    daemon.status()

def version_command(args):
    print 'Janua v%s' % VERSION

def reload_command(args):
    try:
        pid_file = open(config.janua.pid_file, 'r')
    except IOError:
        exit_error('No Janua process running')
    try:
        pid = int(pid_file.read().strip('\n'))
    except ValueError:
        exit_error('No Janua process running')
    pid_file.close()
    try:
        os.kill(pid, signal.SIGHUP)
    except OSError:
        exit_error('No Janua process running')

def action_command(args):
    actions = available_action_dict()
    subcommand = args[args['subcommand']]

    if subcommand != 'admin':
        if not jdb.admin.has_super_admin():
            exit_no_super_admin()
        else:
            update_action_table()

    sadmin = jdb.admin.get_super_admin()
    action = actions[subcommand]
    action_inst = action()
    if subcommand != 'admin':
        action_inst.phone_number = sadmin.phone_number
        action_inst.email = sadmin.email
    try:
        success, message = action_inst.call_console_context(args)
        if not success:
            exit_error(message)
    except ActionError, err:
        exit_error('console context method error: %s' % err)
    except ActionNotifyError, err:
        exit_error('notify method failed: %s', err)
    else:
        error_msg = action_inst.process_notify()
        if error_msg:
            exit_error(error_msg)

        exit_info(message)

def run():
    # log all to file
    arg = ArgParse(prog='janua')

    arg.add_argument('-c', nargs=1, help='Configuration file', metavar='PATH')

    arg.add_section(title='Subcommands', help='subcommand help',
                    dest='subcommand')
    arg.add_section_command('start', description='Start server',
                            callback=start_command)
    arg.add_section_command('stop', description='Stop server',
                            callback=stop_command)
    arg.add_section_command('restart', description='Restart server',
                            callback=restart_command)
    arg.add_section_command('status', description='Server status',
                            callback=status_command)
    arg.add_section_command('version', description='Server version',
                            callback=version_command)
    arg.add_section_command('debug', description='Start with log debug level',
                            callback=debug_command)
    arg.add_section_command('dev', description='Start a development server',
                            callback=dev_command)
    arg.add_section_command('reload', description='Reload custom actions',
                            callback=reload_command)

    sections = [{
        'name': 'action', 'title': 'Specify an action to run', 'desc': '',
        'help': 'Action available', 'callback': action_command,
        'context': 'console'
    }]

    for section in sections:
        arg.add_section_command(
            section['name'],
            title=section['title'],
            description=section['desc'],
            help=section['help'],
            subcommand=True,
            callback=section['callback']
        )
        for action in available_action_list():
            if section['context'] in action.get_contexts():
                arg.add_section_subcommand(action.get_name(),
                                           description=action.get_desc())
                for argument in action.get_arguments():
                    choices = None
                    nargs = 1
                    argtype = str
                    if argument['type'] == 'float':
                        argtype = float
                    if argument['type'] in ['int', 'time']:
                        argtype = int
                    if 'list' in argument['type']:
                        if argument['type'] == 'multilist':
                            nargs = '*'
                        if len(argument['value']) > 0:
                            choices = argument['value']
                    arg.add_section_subcommand_arg(
                        '--' + argument['name'],
                        type=argtype,
                        nargs=nargs,
                        help=argument['desc'],
                        choices=choices,
                        required=not argument['optional']
                    )

    arg.parse_argument()

if __name__ == '__main__':
    run()
