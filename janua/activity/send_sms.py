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
import Queue
import re
import time

import janua.utils.logger as jlogger

from janua.activity.activity import Activity
from janua.db.database import Sms
from janua.sms import SMSError, ModemError
from janua import config, sms_queue, jdb, mail_queue
from janua.utils.utilities import quota_unit
from janua.utils.mail import MailObj, MailError

log = jlogger.getLogger(__name__)

class SendSmsActivity(Activity):
    """
    SMS sender activity
    """
    def __init__(self, sms_interface, *args, **kwargs):
        super(SendSmsActivity, self).__init__(*args, **kwargs)
        self._sms = sms_interface

    def _send_sms(self, message, to, admin):
        sender = u'%s %s' % (admin.firstname, admin.name)
        contact = jdb.contact.get_by_phone(to)
        if not contact:
            contact = jdb.admin.get_by_phone(to)

        if contact:
            ref, slices = self._sms.send(message, contact.phone_number)
            recipient = u'%s %s' % (contact.firstname, contact.name)
            phone_number = contact.phone_number
        else:
            ref, slices = self._sms.send(message, to)
            recipient = to
            phone_number = to

        date = datetime.datetime.now()
        authorized = True
        status = Sms.status_id['SENT']

        jdb.sms.add(
            date.replace(microsecond=0),
            sender,
            recipient,
            message,
            authorized,
            admin.id,
            phone_number,
            status,
            ref,
            slices
        )
        # Don't stress old modems
        time.sleep(config.sms.send_interval)

    def run(self):
        error_counter = 0
        while not self._stopevent.isSet():
            try:
                message, to, admin_id = sms_queue.get(True, 1)
                if not isinstance(admin_id, int):
                    log.error('admin_id is not an integer')
                    continue

                admin = jdb.admin.get_by_id(admin_id)
                if not admin:
                    log.error('Admin id %d not found in database' % admin_id)
                    continue
            except Queue.Empty:
                continue

            sadmin = None
            if isinstance(message, str):
                message = unicode(message, 'utf-8')

            last_notified = admin.last_quota_reached
            if last_notified == None:
                last_notified = datetime.datetime(year=1970, month=1, day=1)
            current = datetime.datetime.now()
            notify = True
            reached, numsms = jdb.sms.is_admin_quota_reached(admin)
            if reached:
                log.debug('%s %s %s' % (admin.firstname, admin.name, admin.sms_quota))
                sadmin = jdb.admin.get_super_admin()
                limit, unit = admin.sms_quota.split(' ')
                if unit == 'D':
                    if last_notified.date() == current.date():
                        notify = False
                elif unit == 'W':
                    current_weekday = current.weekday()
                    last_weekday = last_notified.weekday()
                    current_date = current.date() - datetime.timedelta(days=current_weekday)
                    last_date = last_notified.date() - datetime.timedelta(days=last_weekday)
                    if current_date == last_date:
                        notify = False
                elif unit == 'M':
                    if last_notified.month == current.month and \
                       last_notified.year == current.year:
                        notify = False
                elif unit == 'Y':
                    if last_notified.year == current.year:
                        notify = False
                if notify:
                    data = {
                        'unit': quota_unit[unit],
                        'supervisor': admin.firstname + ' ' + admin.name,
                        'limit': limit,
                    }
                    try:
                        mailobj = MailObj()
                        mailobj.to = admin.email
                        mailobj.template = 'admin_quota_reached'
                        mailobj.template_args = data
                        mailobj.reply_to = sadmin.email
                    except MailError, err:
                        log.critical(err[0])

                    if mail_queue.put(mailobj):
                        log.info('Sending mail to %s, reason: quota reached' % data['supervisor'])

                    admin.last_quota_reached = current
                    jdb.update_entry(admin)
                    log.info('Notifying supervisor %s %s that he '
                              'reached his SMS quota limit'
                              % (admin.firstname, admin.name))
            else:
                try:
                    self._send_sms(message, to, admin)
                    error_counter = 0
                except SMSError, err:
                    log.error(err)
                    # re-queue message when an error occur
                    sms_queue.put([message, to, admin_id])
                    error_counter += 1
                    if error_counter == 10:
                        log.critical('Modem cannot send SMS')
                        time.sleep(60)
                        error_counter = 0
                except ModemError, err:
                    log.critical(err)
                    sms_queue.put([message, to, admin_id])
                    self._sms.reconnect(self._stopevent)
