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

import datetime
import re
import Queue

import janua.utils.logger as jlogger

from janua.actions import ActionNotifyError, ActionError
from janua.actions.action import available_action_list
from janua.activity.activity import Activity
from janua import jdb
from janua.db.database import Sms
from janua.sms import SMSError
from janua.utils.mail import MailError, MailObj
from janua.utils.utilities import get_role

log = jlogger.getLogger(__name__)

class ProcessSmsActivity(Activity):
    """
    SMS processing activity
    """
    def __init__(self, sms_interface, *args, **kwargs):
        super(ProcessSmsActivity, self).__init__(*args, **kwargs)
        self._sms = sms_interface

    def execute_action(self, sms, arguments):
        body = sms['body']
        admin = sms['admin']
        contact = sms['contact']
        sms_action = sms['action']
        phone_number = sms['address']

        try:
            action = sms_action()
            if contact:
                action.phone_number = contact.phone_number
                action.email = contact.email
            elif admin:
                action.phone_number= admin.phone_number
                action.email = admin.email
            else:
                action.phone_number = phone_number
                action.email = None
        except ActionError, err:
            log.critical(err.decode('utf-8'))
            if action:
                del action
            return

        action_name = action.get_name()
        if action.notify == None:
            log.critical('Missing parent __init__ method call in action %s __init__ method' % action_name)
            del action
            return

        if 'sms' in action.get_contexts():
            log.debug('Executing action %s' % action_name)
            try:
                action.call_sms_context(arguments, False)
            except ActionError, err:
                log.error('sms context error: %s' % err)
            except ActionNotifyError, err:
                log.critical('Action notify error: %s' % err)
            except Exception, err:
                log.critical('Bug in action %s: %s' % (action_name, err))

            error_msg = action.process_notify()
            if error_msg:
                log.error(error_msg)

        del action

    def process_id_sms(self, sms):
        phone_number = sms['address']
        admin = sms['admin']
        sms_action = sms['action']
        body = sms['body']

        t = re.compile('(\S+):([-+]?\d+)(:.*)')

        match = t.match(body)
        arguments = []

        if match:
            (password, code, args) = match.groups()
            arguments = re.findall(':([-+]?\d+),([^:]*)', args)
            log.debug('Message received from %s with content: %s%s' % (phone_number, code, args))
        else:
            try:
                (password, code) = body.split(':')[:2]
            except ValueError:
                log.error('Bad message format')
                return

        if password == admin.phone_token or sms_action.get_id() == 0:
            self.execute_action(sms, arguments)
        else:
            log.error('Bad password from %s' % admin.phone_number)

    def process_keyword_sms(self, sms):
        phone_number = sms['address']
        body = sms['body']

        log.debug('Message received from %s with content: %s' % (phone_number, body))

        arguments = [arg for arg in body.split(' ')[1:] if arg != '']
        self.execute_action(sms, arguments)

    def log_sms(self, sms):
        recipient = 'Server'
        phone_number = sms['address']
        date = sms['date']
        body = sms['body']
        authorized = sms['authorized']
        contact = sms['contact']
        admin = sms['admin']
        action = sms['action']

        if contact:
            sender = u'%s %s' % (contact.firstname, contact.name)
        elif admin:
            sender = u'%s %s' % (admin.firstname, admin.name)
            if not action.keyword:
                body = ':'.join(body.split(':')[1:])
        else:
            contact = jdb.contact.get_by_phone(phone_number)
            admin = jdb.admin.get_by_phone(phone_number)
            if contact:
                sender = u'%s %s' % (contact.firstname, contact.name)
            elif admin:
                sender = u'%s %s' % (admin.firstname, admin.name)
            else:
                sender = phone_number

        log.debug('Logging message')
        status = Sms.status_id['RECEIVED']
        try:
            admin_id = jdb.action.get_by_janua_id(action.get_id()).admin_id
        except AttributeError, err:
            # for special get_config action
            admin_id = jdb.admin.get_super_admin().id
        jdb.sms.add(date, sender, recipient, body, authorized, admin_id, phone_number, status=status)

    def authorized(self, sms):
        action = sms['action']
        phone_number = sms['address']
        admin = jdb.admin.get_by_phone(phone_number)

        log.debug('Check sender authorization')

        if not action.keyword:
            if action.get_id() == 0:
                log.debug('Config action triggered by %s' % phone_number)
                if admin:
                    sms['admin'] = admin
                    log.debug('Supervisor authorized to trigger config action')
                    return True
                log.info('Phone number %s asked for sms config' % phone_number)
                return False

            log.debug('Custom action %s triggered by %s' % (action.get_name(), phone_number))
            dbactions = jdb.action.get_all()
            dbactions_id = [act.janua_id for act in dbactions
                                                if act.enabled == True and act.authentication == True]
            if action.get_id() not in dbactions_id:
                log.debug('Action id unknown')
                return False

            if admin:
                sms['admin'] = admin
                if get_role(admin) == 'supervisor':
                    authorized_actions = jdb.action.get_by_authorized_supervisor_id(admin.id)
                    if authorized_actions:
                        log.debug('Supervisor authorized to trigger action')
                        return True
                    log.debug('Supervisor not authorized to trigger action')
                else:
                    log.debug('Super admin authorized to trigger action')
                    return True
        elif action.keyword:
            log.debug('Custom keyword action %s triggered by %s' % (action.keyword, phone_number))

            if admin:
                sms['admin'] = admin
                if action.filtered == False:
                    log.debug('Non filtered action')
                    return True
                if get_role(admin) == 'admin':
                    log.debug('Super admin authorized to trigger action')
                    return True

                authorized_actions = jdb.action.get_by_authorized_supervisor_id(admin.id)

                if action.get_id() in [dbaction.janua_id for dbaction in authorized_actions]:
                    log.debug('Supervisor authorized to trigger action')
                    return True

            db_action = jdb.action.get_by_janua_id(action.get_id())
            if not db_action:
                log.debug('Action keyword not in database')
                return False

            if not action.filtered:
                contact = jdb.contact.get_by_phone(phone_number)
                if contact:
                    sms['contact'] = contact
                log.debug('Action not filtered')
                return True

            contacts = jdb.contact.get_by_action_id(db_action.id)
            try:
                contact = filter(lambda x: x.phone_number == phone_number, contacts)[0]
            except (IndexError, ValueError):
                log.debug('Contact is not authorized to trigger action')
                return False

            if contact:
                sms['contact'] = contact
                log.debug('Contact is authorized to trigger action')
                return True

        return False

    def run(self):
        action_regex = re.compile('([A-Za-z0-9_-]+)([ :]?)')

        while not self._stopevent.isSet():
            try:
                self.queue.get(True, 1)
            except Queue.Empty:
                continue
            else:
                try:
                    smslist = self._sms.process()
                except SMSError, msg:
                    log.critical(msg)
                    continue

                actions = available_action_list()
                action_keyword_dict = dict([(act.get_name(), act) for act in actions
                                            if act.keyword and act.enabled])

                for sms in smslist:
                    if sms['status']:
                        status = sms['status']
                        ref = status['ref']
                        delivered = status['delivered']
                        phone_number = sms['address']

                        smslog = jdb.sms.get_by_ref_and_phone(ref, phone_number)
                        if smslog:
                            smslog.reference = None
                            if delivered:
                                smslog.status = smslog.status_id['SENT/DELIVERED']
                            else:
                                smslog.status = smslog.status_id['SENT/UNKNOWN']

                        if not jdb.update_entry(smslog):
                            log.error('Couldn\'t update sms status')
                        continue

                    sms.update({
                        'admin': None,
                        'contact': None,
                        'action': None,
                        'authorized': False
                    })

                    if not isinstance(sms['body'], basestring):
                        sms['body'] = str(sms['body'])

                    match_action = action_regex.match(sms['body'])

                    if match_action:
                        action_keyword, _ = match_action.groups()
                        action_keyword = action_keyword.lower()
                        if action_keyword not in action_keyword_dict:
                            try:
                                _, action_id = sms['body'].split(':')[:2]
                            except ValueError:
                                log.error('Bad sms format')
                            else:
                                try:
                                    action_id = int(action_id, 10)
                                except ValueError:
                                    log.error('Bad action id format')
                                else:
                                    action_dict = dict([(act.get_id(), act) for act in actions
                                                         if (not act.keyword and act.enabled) or act.get_id() == 0])
                                    try:
                                        action = action_dict[action_id]
                                    except IndexError, err:
                                        log.info('Bad action id')
                                        self.log_sms(sms)
                                        continue

                                    sms['action'] = action
                                    if self.authorized(sms):
                                        sms['authorized'] = True
                                        self.process_id_sms(sms)
                                    else:
                                        log.info('Message refused from %s' % sms['address'])
                        else:
                            sms['action'] = action_keyword_dict[action_keyword]
                            if self.authorized(sms):
                                sms['authorized'] = True
                                self.process_keyword_sms(sms)
                            else:
                                log.info('Message refused from %s' % sms['address'])
                    else:
                        log.error('Bad sms format')

                    self.log_sms(sms)
                del smslist
