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

import csv
import datetime
import cStringIO
import sys

from janua import jdb
from janua.actions.action import Action, argument, date
from janua.actions.action import console_error, console_success
from janua.db.database import Sms
from janua.utils.utilities import prompt

class Log(Action):
    """
    Extract log from database in CSV format
    """

    category = '__INTERNAL__'

    def display_log(self, entries):
        output_file = self.output()
        output = cStringIO.StringIO()

        output.write('Date;recipient;sender;message;status;authorized\n')

        status_id = sorted(Sms.status_id.items(), key=lambda x: x[1])
        count = 0
        for entry in entries:
            date = entry.date_time.strftime('%Y-%m-%d %H:%M:%S')
            authorized = 'yes' if entry.authorized else 'no'
            sender = entry.sender
            recipient = entry.recipient
            message = entry.raw_message
            status = status_id[entry.status][0]
            line = '%s;%s;%s;%s;%s;%s\n' % (date, sender, recipient,
                                         message, status, authorized)
            output.write(line.encode('utf-8'))
            count += 1

        if output_file:
            outfile = open(output_file, 'w')
            outfile.write(output.getvalue())
            outfile.close()
            return console_success('File %s was created' % output_file)
        else:
            print output.getvalue()
            return console_success('%d lines displayed' % count)

    def view_log(self, start, end):
        entries = jdb.sms.get_by_date(startdate=start, enddate=end)
        return self.display_log(entries)

    def delete_log(self, start, end):
        if not end:
            return console_error('You must specify at least end date')
        else:
            jdb.sms.delete(start, end)
            return console_success('Logs have been deleted')

    def view_admin_log(self, start, end):
        admins = jdb.admin.get_all()
        print 'Select an admin number to display only these logs :'
        idx = 0
        for admin in admins:
            print '%d. %s %s' % (idx, admin.firstname, admin.name)
            idx += 1
        admin_id = prompt('Enter a number (or ENTER to quit)')
        if admin_id == '':
            return console_success('exit')

        if admin_id.isdigit():
            admin_id = admins[int(admin_id)].id
            entries = jdb.sms.get_by_admin(
                admin_id, startdate=start, enddate=end
            )
            return self.display_log(entries)
        else:
            return console_error('the value entered is not a number')

    def console(self):
        op = self.operation()
        startdate = None
        enddate = None

        if self.startdate():
            startdate = datetime.datetime.strptime(self.startdate(), '%Y/%m/%d')
        if self.enddate():
            enddate = datetime.datetime.strptime(self.enddate(), '%Y/%m/%d')
            enddate += datetime.timedelta(days=1)

        if op == 'view':
            return self.view_log(startdate, enddate)
        elif op == 'delete':
            return self.delete_log(startdate, enddate)
        elif op == 'view_admin':
            return self.view_admin_log(startdate, enddate)

    @argument(required=True)
    def operation(self):
        """Operation: view, delete, adminview"""
        return ['view', 'delete', 'view_admin']

    @argument(required=False)
    def output(self):
        """output file"""
        return ''

    @argument(required=False)
    def startdate(self):
        """From date (date format: YYYY/MM/DD)"""
        return date()

    @argument(required=False)
    def enddate(self):
        """To date (date format: YYYY/MM/DD)"""
        return date()
