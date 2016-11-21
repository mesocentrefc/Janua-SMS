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
Janua database API
"""

import calendar
import datetime
import os
from sqlalchemy import event

from janua.utils.utilities import get_role
from janua.db.database import Admin, Action, Base, Config, Commands
from janua.db.database import Sms, Group
from janua.db.database import AuthorizedGroupAction, AuthorizedSupervisorAction
from janua.db.database import ContactNotifyAction, Contact, ContactGroup

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, func

class ObjectDB(object):
    """
    Generic class to connect database APIs to :class:`.JanuaDB`
    """
    def __init__(self, db):
        """
        Constructor

        :param db: JanuaDB instance
        """
        self.session = db.session
        self.db = db

class ConfigDB(ObjectDB):
    """
    Config database API
    """
    def add(self, key, value):
        """
        Add a Config entry object

        :param key: configuration
        :param value: configuration value
        :returns: True if entry was added or False if wasn't
        """
        config = Config(key=key, value=value)
        return self.db.add_entry(config)

    def delete(self, key):
        """
        Delete a Config entry object

        :param key: key entry to delete
        :returns: True if entry was deleted or False if wasn't
        """
        config = self.session.query(Config).filter(Config.key==key).first()
        return self.db.del_entry(config)

    def get(self, key):
        """
        Get a Config entry object identified by key

        :param key: config key entry to get
        :returns: Config entry object
        """
        return self.session.query(Config).filter(Config.key==key).first()


class SmsDB(ObjectDB):
    def add(self, date, sender, recipient, message, authorized, admin_id, phone_number, status=3, reference=None, slices=1):
        """
        Add a sms log entry

        :param date: date time
        :param sender: sender address, name or ip address
        :param recipient: recipient address or name
        :param message: message in raw format (mainly for debug purpose)
        :param authorized: is sender authorized to send SMS to server
        :param admin_id: admin send message, for received message default to super admin
        :param phone_number: recipient phone number
        :param status: sms status
        :param reference: reference for delivery report
        :param slices: number of slices (for multi-part SMS)
        :returns: True if entry was added or False if wasn't
        """
        sms = Sms(
            date_time=date,
            sender=sender,
            recipient=recipient,
            raw_message=message,
            authorized=authorized,
            status=status,
            reference=reference,
            admin_id=admin_id,
            recipient_phone_number=phone_number,
            number_of_slices=slices
        )
        return self.db.add_entry(sms)

    def get_by_admin(self, admin_id, startdate=None, enddate=None):
        """
        Get sms log entries by admin

        :param startdate: get entries from date (datetime argument)
        :param enddate: get entries to date (datetime argument)
        :param admin_id: admin identifier
        :returns: all Log entry object
        """
        if startdate and enddate:
            return self.session.query(Sms).\
                   filter((Sms.date_time.between(startdate, enddate)) & (Sms.admin_id==admin_id)).\
                   all()
        elif startdate and not enddate:
            end = datetime.datetime.now()
            return self.session.query(Sms).\
                   filter((Sms.date_time.between(startdate, end)) & (Sms.admin_id==admin_id)).\
                   all()
        elif enddate and not startdate:
            return self.session.query(Sms).\
                   filter((Sms.date_time<=enddate) & (Sms.admin_id==admin_id)).\
                   all()
        else:
            return self.session.query(Sms).\
                   filter(Sms.admin_id==admin_id).\
                   all()

    def get_by_date(self, startdate=None, enddate=None):
        """
        Get sms log entries

        :param startdate: get entries from date (datetime argument)
        :param enddate: get entries to date (datetime argument)
        :returns: all Log entry object
        """
        if startdate and enddate:
            return self.session.query(Sms).\
                   filter(Sms.date_time.between(startdate, enddate)).\
                   all()
        elif startdate and not enddate:
            end = datetime.datetime.now()
            return self.session.query(Sms).\
                   filter(Sms.date_time.between(startdate, end)).\
                   all()
        elif enddate and not startdate:
            return self.session.query(Sms).\
                   filter(Sms.date_time<=enddate).\
                   all()
        else:
            return self.session.query(Sms).all()

    def get_by_ref_and_phone(self, ref, phone_number):
        """
        Get sms log entry by recipient phone number and sms reference

        :param ref: sms reference
        :param phone_number: recipient phone number
        :returns: corresponding sms log entry object
        """
        return self.session.query(Sms).\
               filter((Sms.reference==ref) & (Sms.recipient_phone_number==phone_number)).\
               order_by(Sms.date_time.desc()).\
               first()

    def delete(self, startdate, enddate):
        """
        Delete sms log entries in a date interval

        :param startdate: delete entries from date (datetime argument)
        :param enddate: delete entries to date (datetime argument)
        :returns: all Log entry object
        """
        if startdate and enddate:
            self.session.query(Sms).\
                filter(Sms.date_time.between(startdate, enddate)).\
                delete(synchronize_session=False)
            self.session.commit()
        elif startdate and not enddate:
            end = datetime.datetime.now()
            self.session.query(Sms).\
                filter(Sms.date_time.between(startdate, end)).\
                delete()
            self.session.commit()
        elif enddate and not startdate:
            self.session.query(Sms).\
                filter(Sms.date_time<=enddate).\
                delete()
            self.session.commit()

    def is_admin_quota_reached(self, admin):
        """
        Test if sms send limit has been reached for admin

        :param admin: admin entry
        :returns: a tuple of 2 value, first value indicate if limit has been
                  reached, second value indicate the number of sms sent
        """
        sms_quota = admin.sms_quota
        admin_id = admin.id
        quota, unit = sms_quota.split(' ')
        quota = int(quota)

        current = datetime.datetime.now()
        year = current.year
        month = current.month
        day = current.day

        if unit == 'D':
            start = datetime.datetime(year=year, month=month, day=day)
            end = start + datetime.timedelta(days=1)
        if unit == 'W':
            weekday = current.weekday()
            start_monday = day - weekday
            start = datetime.datetime(year=year, month=month, day=start_monday)
            end = start + datetime.timedelta(days=7)
        if unit == 'M':
            start = datetime.datetime(year=year, month=month, day=1)
            maxday = calendar.monthrange(current.year, current.month)[1]
            end = datetime.datetime(year=year, month=month, day=maxday)
            end += datetime.timedelta(days=1)
        if unit == 'Y':
            start = datetime.datetime(year=year, month=1, day=1)
            end = datetime.datetime(year=year+1, month=1, day=1)

        count = self.session.query(func.total(Sms.number_of_slices)).\
                             filter((Sms.admin_id==admin_id) & (Sms.date_time.between(start, end)) & (Sms.status <= 2)).\
                             first()[0]
        if count >= quota:
            return True, count

        return False, count

    def month_usage(self):
        """
        Get sms sent count sent for current month

        :returns: number of sms sent
        """
        current = datetime.datetime.now()
        month = current.month
        year = current.year

        start = datetime.datetime(year=year, month=month, day=1)
        maxday = calendar.monthrange(year, month)[1]
        end = datetime.datetime(year=year, month=month, day=maxday)
        end += datetime.timedelta(days=1)
        count = self.session.query(func.total(Sms.number_of_slices)).\
                             filter((Sms.date_time.between(start, end)) & (Sms.status <= 2)).\
                             first()[0]
        return count


    def get_admin_month_stats(self, admin):
        """
        Get SMS month statistics usage for an admin

        :param admin: admin object
        :returns: a list containing dictionary with month/value keys
                  representing number of SMS sent corresponding month
        """
        data = []
        if get_role(admin) == 'admin':
            admin_filter = ''
        else:
            admin_filter = 'AND admin_id = %s' % admin.id

        res = self.db.engine.execute("""
        SELECT
            strftime('%m', date_time) as yr_mon,
            TOTAL(number_of_slices) as sms
        FROM SMS
            WHERE status <= 2 AND strftime('%Y', date_time) = '{0}' {1}
        GROUP BY yr_mon
        ORDER BY yr_mon""".format((datetime.datetime.now().year), admin_filter))

        last_month = 0
        for month_id in xrange(1, 13):
            data.append({
                'month': calendar.month_abbr[month_id],
                'value': 0
            })

        for row in res.fetchall():
            month_id = int(row[0])
            data[month_id-1]['value'] = int(row[1])
        return data

class ContactDB(ObjectDB):
    def add(self, name, firstname, phone):
        """
        Add a contact

        :param name: contact name
        :param firstname: contact firstname
        :param phone_number: contact phone number
        :returns: True if entry was added or False if wasn't
        """
        contact = Contact(name=name, firstname=firstname, phone_number=phone)
        return self.db.add_entry(contact)

    def delete(self, id):
        """
        Delete a contact

        :param id: id primary key
        :returns: True if entry was deleted or False if wasn't
        """
        contact = self.session.query(Contact).filter(Contact.id==id).first()
        return self.db.del_entry(contact)

    def get_all(self):
        """
        Get all contact entry

        :returns: all Contact entry object
        """
        return self.session.query(Contact).all()

    def get_by_id(self, id):
        """
        Get a Contact entry corresponding to id

        :returns: a Contact entry object
        """
        return self.session.query(Contact).filter(Contact.id==id).first()

    def get_by_phone(self, phone):
        """
        Get a Contact entry corresponding to phone number

        :returns: a Contact entry object
        """
        return self.session.query(Contact).filter(Contact.phone_number==phone).first()

    def get_by_group_id(self, group_id):
        """
        Get all contact entries corresponding to group id

        :param group_ids: group_id list
        :returns: Contact entries object
        """
        if len(group_id) == 0:
            return group_id
        return self.session.query(Contact).\
                            join(ContactGroup, Contact.id==ContactGroup.contact_id).\
                            join(Group, ContactGroup.group_id==Group.id).\
                            filter(Group.id.in_(group_id)).\
                            all()

    def get_by_admin_phone(self, phone_number):
        """
        Get all contact entry managed by an admin which is identified by his phone number

        :param phone_number: admin phone number
        :returns: Contact entry object managed by admin
        """
        admin = self.db.admin.get_by_phone(phone_number)

        if not admin:
            return []

        return self.session.query(Contact).\
                            filter(Contact.admin_id==admin.id).\
                            all()

    def get_by_action_id(self, action_id):
        """
        Get all contact entries affected to an action

        :param action_id: action database id
        :returns: Contact entries object
        """
        return self.session.query(Contact).\
               join(ContactGroup, Contact.id==ContactGroup.contact_id).\
               join(AuthorizedGroupAction, ContactGroup.group_id==AuthorizedGroupAction.group_id).\
               filter(AuthorizedGroupAction.action_id==action_id).\
               all()

class AdminDB(ObjectDB):
    def has_super_admin(self):
        """
        Check if there a superadmin entry in database

        :returns: True if yes or False if not
        """
        admin = self.session.query(Admin).filter(Admin.level==1).first()
        if admin:
            return True
        return False

    def get_super_admin(self):
        """
        Get superadmin entry

        :returns: Admin entry object
        """
        return self.session.query(Admin).filter(Admin.level==1).first()

    def get_by_phone(self, phone_number):
        """
        Get an admin entry by phone number

        :param phone_number: admin phone number
        :returns: an Admin entry object
        """
        return self.session.query(Admin).\
                            filter(Admin.phone_number==phone_number).\
                            first()

    def get_by_login(self, login):
        """
        Get an admin entry by login

        :param phone_number: admin login
        :returns: an Admin entry object
        """
        return self.session.query(Admin).\
                            filter(Admin.login==login).\
                            first()

    def get_by_mail(self, mail):
        """
        Get an admin entry by mail

        :param phone_number: admin mail
        :returns: an Admin entry object
        """
        return self.session.query(Admin).\
                            filter(Admin.email==mail).\
                            first()

    def get_by_id(self, id):
        """
        Get admin entry by id

        :param id: admin id
        :returns: an Admin entry object
        """
        return self.session.query(Admin).\
               filter(Admin.id==id).\
               first()

    def get_all(self):
        """
        Get all admin entry

        :returns: all Admin entry object
        """
        return self.session.query(Admin).all()

    def add(self, firstname, name, phone_number, password, email, level, login):
        """
        Add an admin/supervisor

        :param name: admin name
        :param firstname: admin firstname
        :param phone_number: admin phone number
        :param password: hashed sha password
        :param email: admin/supervisor email
        :param level: 1 for admin, 2 for supervisor
        :param login: user login
        :returns: True if entry was added or False if wasn't
        """
        admin = Admin(firstname=firstname, name=name, phone_number=phone_number,
                      password=password, email=email, level=level, login=login)
        return self.db.add_entry(admin)

    def get_level(self, phone_number):
        """
        Get admin level based on phone number aka username credential

        :param phone_number: phone number as credential
        :returns: admin level or None
        """
        admin = self.db.admin.get_by_phone(phone_number)

        if admin:
            return admin.level

        return None

    def get_id_from_phone(self, phone_number):
        """
        Get admin id base on phone number aka username credential

        :param phone_number: phone number as credential
        :returns: admin id or None
        """
        admin = self.db.admin.get_by_phone(phone_number)

        if admin:
            return admin.id

        return None

class ContactGroupDB(ObjectDB):
    def get_by_group_id(self, group_id):
        """
        Get contact group entries

        :param group_ids: group id list corresponding to entry to retrieve
        :returns: ContactGroup entry object
        """
        if len(group_id) == 0:
            return group_id
        return self.session.query(ContactGroup).\
                            filter(ContactGroup.group_id.in_(group_id)).\
                            all()

class GroupDB(ObjectDB):
    def get_by_contact_id(self, contact_id):
        """
        Get group entries for contact id

        :param contact_id: contact id
        :returns: Group entry object
        """
        return self.session.query(Group).\
                            join(ContactGroup, ContactGroup.group_id==Group.id).\
                            filter(ContactGroup.contact_id==contact_id).\
                            all()

    def get_by_admin_phone(self, phone_number):
        """
        Get all group entries managed by an admin which is identified by his phone number

        :param phone_number: admin phone number
        :returns: Group entries object managed by admin
        """
        return self.session.query(Group).\
                            join(Admin, Group.admin_id==Admin.id).\
                            filter(Admin.phone_number==phone_number).\
                            all()

class AuthorizedGroupDB(ObjectDB):
    def get_by_admin_id(self, admin_id):
        """
        Get all authorized group entries managed by an admin

        :param admin_id: admin id
        :returns: AuthorizedGroupAction entry object managed by admin
        """
        return self.session.query(AuthorizedGroupAction).\
               join(Action, AuthorizedGroupAction.action_id==Action.id).\
               filter(Action.admin_id==admin_id).\
               all()

class ActionDB(ObjectDB):
    def add(self, name, module, description, authentication, enabled, janua_id):
        """
        Add an action

        :param name: action name
        :param module: python module namespace of action
        :param description: action description
        :param authentication: is action require authentication
        :param janua_id: action internal id
        :returns: True if added, False otherwise
        """
        super_admin = self.db.admin.get_super_admin()
        if super_admin:
            admin_id = super_admin.id
            action = Action(name=name, module=module,
                            authentication=authentication,
                            description=description, admin_id=admin_id,
                            janua_id=janua_id, enabled=enabled)

            return self.db.add_entry(action)
        else:
            return False

    def get_all(self):
        """
        Get all action entries

        :returns: Action entries object
        """
        return self.session.query(Action).all()

    def get_by_janua_id(self, id):
        """
        Get action entry by janua action id

        :param id: janua internal id (janua_id)
        :returns: Action entry object
        """
        return self.session.query(Action).\
               filter(Action.janua_id==id).\
               first()

    def get_by_authorized_supervisor_id(self, admin_id):
        """
        Get all authorized supervisor action

        :param admin_id: admin id
        :returns: Action entries object
        """
        return self.session.query(Action).\
               join(AuthorizedSupervisorAction, AuthorizedSupervisorAction.action_id==Action.id).\
               filter(AuthorizedSupervisorAction.admin_id==admin_id).\
               all()

class ContactNotifyDB(ObjectDB):
    def get_by_admin_id(self, admin_id):
        """
        Get all contact notify entries managed by an admin

        :param admin_id: admin id
        :returns: ContactNotifyAction entries object
        """
        return self.session.query(ContactNotifyAction).\
               join(Action, ContactNotifyAction.action_id==Action.id).\
               filter(Action.admin_id==admin_id).\
               all()

    def get_by_action_id(self, action_id):
        """
        Get contact notify action assigned to an action

        :param action_id: action id
        :returns: ContactNotifyAction entries
        """
        return self.session.query(ContactNotifyAction).\
               filter(ContactNotifyAction.action_id==action_id).\
               all()

class CommandsDB(ObjectDB):
    def get_all(self):
        """
        Get all commands

        :returns: Commands entries object
        """
        return self.session.query(Commands).all()

class JanuaDB(object):
    """
    Janua database instance
    """

    engine = None
    """Sqlalchemy engine"""

    session = None
    """Thread-safe sqlalchemy session"""

    admin = None
    """Admin database object (:class:`.AdminDB`)"""

    contact = None
    """Contact database object (:class:`.ContactDB`)"""

    sms = None
    """Sms database object (:class:`.SmsDB`)"""

    config = None
    """Config data object (:class:`.ConfigDB`)"""

    action = None
    """Action database object (:class:`.ActionDB`)"""

    commands = None
    """Commands database object (:class:`.CommandsDB`)"""

    contact_notify = None
    """Contact notify action database object (:class:`.ContactNotifyDB`)"""

    contact_group = None
    """Contact group database object (:class:`.ContactGroupDB`)"""

    authorized_group = None
    """Authorized group action database object (:class:`.AuthorizedGroupDB`)"""

    group = None
    """Group database object (:class:`.GroupDB`)"""

    def __init__(self, januadb_file):
        """
        Initialize connection to database and create it if it doesn't exists

        :param januadb_file: janua sqlite database file
        """
        self.januadb_file = januadb_file
        self.januadb_uri = 'sqlite:///%s?check_same_thread=False' % (self.januadb_file)
        self.engine = self.create_db()
        self.session = scoped_session(sessionmaker(bind=self.engine, autocommit=False, autoflush=False))

        self.admin = AdminDB(self)
        self.contact = ContactDB(self)
        self.sms = SmsDB(self)
        self.config = ConfigDB(self)
        self.action = ActionDB(self)
        self.commands = CommandsDB(self)
        self.contact_notify = ContactNotifyDB(self)
        self.contact_group = ContactGroupDB(self)
        self.authorized_group = AuthorizedGroupDB(self)
        self.group = GroupDB(self)

    def create_db(self):
        """
        Create database if it doesn't exists

        :returns: sqlalchemy engine
        """
        engine = create_engine(self.januadb_uri, convert_unicode=True, pool_recycle=3600, echo=False)
        if not os.path.exists(self.januadb_file):
            Base.metadata.create_all(engine)
        return engine

    def create_table(self, table):
        """
        Create a table in Janua database

        :param table: table model
        """
        return table.__table__.create(self.engine, checkfirst=True)

    def add_entry(self, obj):
        """
        Add an object entry

        :param obj: entry object to add
        :returns: True if entry was added, False otherwise
        """
        try:
            self.session.add(obj)
            self.session.commit()
        except:
            self.session.rollback()
            return False

        return True

    def del_entry(self, obj):
        """
        Delete an object entry

        :param obj: entry object to delete
        :returns: True if entry was deleted, False otherwise
        """
        try:
            self.session.delete(obj)
            self.session.commit()
        except:
            self.session.rollback()
            return False

        return True

    def update_entry(self, obj):
        """
        Update an object entry

        :param obj: entry object to update
        :returns: True if entry was updated, False otherwise
        """
        try:
            self.session.commit()
        except:
            self.session.rollback()
            return False
        return True
