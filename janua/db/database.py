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

from sqlalchemy import Boolean, Column, DateTime, Enum, DDL, ForeignKey
from sqlalchemy import Integer, String, Text, event, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

class DefaultTableArgsBase(object):
    """Base class for SQLAlchemy model classes."""
    __table_args__ = {'useexisting': True}

# if an action module has to specify __table_args__ for special purpose
# don't forget to define it as a tuple like this:
# __table_args__ = (
#    UniqueConstraint('form_id', 'event_id'),
#    Base.__table_args__
# )
Base = declarative_base(cls=DefaultTableArgsBase)

class Config(Base):
    """
    Config database model
    """
    __tablename__ = 'CONFIG'

    key = Column(Text, primary_key=True, unique=True)
    """configuration key parameter"""

    value = Column(Text, nullable=False)
    """configuration key value"""

class Contact(Base):
    """
    Contact database model

    **Unique constraints:**
      * unique tuple of phone number and admin id
      * unique tuple of email and admin id
    """
    __tablename__ = 'CONTACT'
    __table_args__ = (
        UniqueConstraint(
            'phone_number', 'admin_id', name='_unique_phone_number_byadmin'
        ),
        UniqueConstraint(
            'email', 'admin_id', name='_unique_mail_byadmin'
        ),
        Base.__table_args__
    )

    id = Column(Integer, primary_key=True)
    """primary key id"""

    name = Column(String(255), nullable=False)
    """contact name"""

    firstname = Column(String(255), nullable=False)
    """contact firstname"""

    phone_number = Column(String(25), nullable=False)
    """contact phone number"""

    email = Column(String(255), nullable=False)
    """contact email"""

    description = Column(Text, nullable=True)
    """contact description"""

    admin_id = Column(ForeignKey('ADMIN.id'), unique=False, nullable=False)
    """id of admin which manage this contact"""

    groups = relationship(u'Group', secondary='CONTACT_GROUP', viewonly=True)
    """group list in which this contact belong to"""

    @hybrid_property
    def fullname(self):
        """return concatenate string of firstname and name"""
        return self.firstname + ' ' + self.name

class Sms(Base):
    """
    SMS log database model
    """
    __tablename__ = 'SMS'

    id = Column(Integer, primary_key=True)
    """primary key id"""

    date_time = Column(DateTime, nullable=False)
    """store received or send sms date time"""

    sender = Column(Text, nullable=False)
    """fullname sender"""

    recipient = Column(Text, nullable=False)
    """fullname recipient"""

    recipient_phone_number = Column(String(25), nullable=False)
    """recipient phone number"""

    raw_message = Column(Text, nullable=False)
    """message body"""

    authorized = Column(Boolean, nullable=False)
    """whitelisted or blacklisted"""

    status = Column(Integer, nullable=False, default=3)
    """
    SMS status. Corresponding values:
      0. SENT
      1. SENT/DELIVERED
      2. SENT/UNKNOWN
      3. UNSUPPORTED
      4. RECEIVED
    """

    reference = Column(Integer, nullable=True)
    """reference id for concatenated SMS"""

    number_of_slices = Column(Integer, nullable=False, default=1)
    """number of SMS chunks"""

    admin_id = Column(ForeignKey('ADMIN.id'), unique=False, nullable=False)
    """admin which send the SMS"""

    status_id = {
        'SENT': 0,
        'SENT/DELIVERED': 1,
        'SENT/UNKNOWN': 2,
        'UNSUPPORTED': 3,
        'RECEIVED': 4
    }

class Group(Base):
    """
    Group database model

    **Unique constraint:**
      * unique tuple of name and admin id
    """
    __tablename__ = 'GROUPS'
    __table_args__ = (
        UniqueConstraint(
            'name', 'admin_id', name='_unique_group_name_byadmin'
        ),
        Base.__table_args__
    )

    id = Column(Integer, primary_key=True)
    """primary key id"""

    name = Column(String(255), nullable=False)
    """group name"""

    description = Column(Text, nullable=False, default='')
    """group description"""

    admin_id = Column(ForeignKey('ADMIN.id'), unique=False, nullable=False)
    """admin which manage this group"""

    contacts = relationship(
        u'Contact',
        secondary='CONTACT_GROUP', viewonly=True
    )
    """contact which belong to this group"""

    actions = relationship(
        u'Action',
        secondary='AUTHORIZED_GROUP_ACTION',
        viewonly=True
    )
    """actions this group have permission to trigger"""

class ContactGroup(Base):
    """
    Contact group relation database model

    **Unique constraint:**
      * unique tuple of group and contact id
    """
    __tablename__ = 'CONTACT_GROUP'
    __table_args__ = (
        UniqueConstraint('group_id', 'contact_id', name='_contactgroup'),
        Base.__table_args__
    )

    id = Column(Integer, primary_key=True)
    """primary key id"""

    group_id = Column(ForeignKey('GROUPS.id'), unique=False, nullable=False)
    """group id foreign key"""

    contact_id = Column(ForeignKey('CONTACT.id'), unique=False, nullable=False)
    """contact id foreign key"""

# Admin level
# 1: admin
# 2: supervisor
class Admin(Base):
    """
    Admin database model
    """
    __tablename__ = 'ADMIN'

    id = Column(Integer, primary_key=True)
    """primary key id"""

    name = Column(String(255), nullable=False)
    """administrator name"""

    firstname = Column(String(255), nullable=False)
    """administrator firstname"""

    phone_number = Column(String(25), nullable=False, unique=True)
    """administrator phone number, **should be unique**"""

    has_client = Column(Boolean, nullable=False, default=False)
    """is administrator have Janua client ?"""

    password = Column(String(255), nullable=False)
    """administrator encrypted password"""

    email = Column(String(255), nullable=False, unique=True)
    """administrator email, **should be unique**"""

    level = Column(Integer, nullable=False)
    """
    administrator level:
      1. super administrator
      2. supervisor
    """

    sms_quota = Column(String(10), nullable=False, default='100 M')
    """
    administrator SMS quota of the form "number X" where X could take:
      * **D**: mean number per day
      * **W**: mean number per week
      * **M**: mean number per month
      * **Y**: mean number per year
    """

    recipient_filter = Column(Boolean, nullable=False, default=True)
    """is administrator restricted to whitelist or can send to any recipients"""

    last_quota_reached = Column(DateTime, nullable=True)
    """when administrator has been last notified about reached sms quota"""

    login = Column(String(255), nullable=False, unique=True)
    """administrator login, **should be unique**"""

    phone_token = Column(String(10), nullable=True, unique=True)
    """administrator phone token, used by Janua client, **should be unique**"""

    web_auth_token = Column(String(255), nullable=True, unique=True)
    """administrator web token, for web interface and REST API, **should be unique**"""

    auth_backend = Column(Text, nullable=False, default='local')
    """which authentication backend does it use"""

    @hybrid_property
    def fullname(self):
        """return concatenate string of firstname and name"""
        return self.firstname + ' ' + self.name

class Action(Base):
    """
    Action database model
    """
    __tablename__ = 'ACTION'

    id = Column(Integer, primary_key=True)
    """primarey id key"""

    name = Column(String(255), nullable=False, unique=True)
    """action name, obtained by lower action class name string, **should be unique**"""

    description = Column(Text, nullable=False)
    """action description, obtained by taking action class docstring"""

    module = Column(String(255), nullable=False, unique=True)
    """action module path, **should be unique**"""

    authentication = Column(Boolean, nullable=False, default=False)
    """is action require authentication"""

    enabled = Column(Boolean, nullable=False, default=True)
    """is action enabled"""

    admin_id = Column(ForeignKey('ADMIN.id'), unique=False, nullable=False)
    """admin who manage this action"""

    janua_id = Column(Integer, nullable=False, unique=True)
    """unique id for internal use, **don't touch this**"""

    admin = relationship(u'Admin')
    """admin object"""

    authorized_group = relationship(
        u'Group',
        secondary='AUTHORIZED_GROUP_ACTION',
        viewonly=True
    )
    """groups object which are authorized to trigger action"""

    authorized_supervisor = relationship(
        u'Admin',
        secondary='AUTHORIZED_SUPERVISOR_ACTION',
        viewonly=True
    )
    """administrator object which are authorized to trigger action"""

    contact_notify = relationship(
        u'Contact',
        secondary='CONTACT_NOTIFY_ACTION',
        viewonly=True
    )
    """contact notify object"""

class AuthorizedGroupAction(Base):
    """
    Authorized group action database model

    **Unique constraint:**
      * unique tuple of group and action id
    """
    __tablename__ = 'AUTHORIZED_GROUP_ACTION'
    __table_args__ = (
        UniqueConstraint(
            'group_id', 'action_id', name='_authorized_group_action'
        ),
        Base.__table_args__
    )

    id = Column(Integer, primary_key=True)
    """primary key id"""

    group_id = Column(ForeignKey('GROUPS.id'), unique=False)
    """group id foreign key"""

    action_id = Column(ForeignKey('ACTION.id'), unique=False)
    """action id foreign key"""

class AuthorizedSupervisorAction(Base):
    """
    Authorized administrator action database model

    **Unique constraint:**
      * unique tuple of admin and action id
    """

    __tablename__ = 'AUTHORIZED_SUPERVISOR_ACTION'
    __table_args__ = (
        UniqueConstraint(
            'admin_id', 'action_id', name='_authorized_supervisor_action'
            ),
        Base.__table_args__
    )

    id = Column(Integer, primary_key=True)
    """primary key id"""

    admin_id = Column(ForeignKey('ADMIN.id'), unique=False, nullable=False)
    """admin id foreign key"""

    action_id = Column(ForeignKey('ACTION.id'), unique=False, nullable=False)
    """action id foreign key"""

class ContactNotifyAction(Base):
    """
    Contact notify action database model

    **Unique constraint:**
      * unique tuple of contact, action and group id
    """

    __tablename__ = 'CONTACT_NOTIFY_ACTION'
    __table_args__ = (
        UniqueConstraint(
            'contact_id', 'action_id', 'group_id', name='_contact_notify_action'
        ),
        Base.__table_args__
    )

    id = Column(Integer, primary_key=True)
    """primary key id"""

    contact_id = Column(ForeignKey('CONTACT.id'), unique=False, nullable=False)
    """contact id foreign key"""

    action_id = Column(ForeignKey('ACTION.id'), unique=False, nullable=False)
    """action id foreign key"""

    group_id = Column(ForeignKey('GROUPS.id'), unique=False, nullable=False)
    """group id foreign key"""

class Commands(Base):
    """
    Command database model
    """
    __tablename__ = 'COMMANDS'

    id = Column(Integer, primary_key=True)
    """primary key id"""

    command = Column(Text, nullable=False)
    """command string identifier"""

    params = Column(Text, nullable=False)
    """command parameters in JSON format"""

delete_group_trigger = DDL("""
CREATE TRIGGER delete_group
AFTER DELETE ON GROUPS
FOR EACH ROW
BEGIN
    DELETE from CONTACT_GROUP WHERE group_id = OLD.id;
    DELETE from AUTHORIZED_GROUP_ACTION WHERE group_id = OLD.id;
END;""")

delete_contact_trigger = DDL("""
CREATE TRIGGER delete_contact
AFTER DELETE ON CONTACT
FOR EACH ROW
BEGIN
    DELETE from CONTACT_GROUP WHERE contact_id = OLD.id;
END;""")

delete_contact_group_trigger = DDL("""
CREATE TRIGGER delete_contact_group
AFTER DELETE ON CONTACT_GROUP
FOR EACH ROW
BEGIN
    DELETE from CONTACT_NOTIFY_ACTION WHERE contact_id = OLD.contact_id AND group_id = OLD.group_id;
END;""")

delete_authorized_group_action_trigger = DDL("""
CREATE TRIGGER delete_authorized_group_action
AFTER DELETE ON AUTHORIZED_GROUP_ACTION
FOR EACH ROW
BEGIN
    DELETE from CONTACT_NOTIFY_ACTION
    WHERE contact_id IN
    (
        SELECT contact_id FROM CONTACT_GROUP WHERE group_id = OLD.group_id
    ) AND group_id = OLD.group_id AND action_id = OLD.action_id;
END;""")

delete_action_trigger = DDL("""
CREATE TRIGGER delete_action
AFTER DELETE ON ACTION
FOR EACH ROW
BEGIN
    DELETE from AUTHORIZED_GROUP_ACTION WHERE action_id = OLD.id;
    DELETE from AUTHORIZED_SUPERVISOR_ACTION WHERE action_id = OLD.id;
    DELETE from CONTACT_NOTIFY_ACTION WHERE action_id = OLD.id;
END;""")

update_action_trigger = DDL("""
CREATE TRIGGER update_action
AFTER UPDATE OF admin_id ON ACTION
FOR EACH ROW
WHEN OLD.admin_id <> NEW.admin_id
BEGIN
    DELETE from AUTHORIZED_GROUP_ACTION WHERE action_id = OLD.id;
    DELETE from AUTHORIZED_SUPERVISOR_ACTION WHERE action_id = OLD.id;
    DELETE from CONTACT_NOTIFY_ACTION WHERE action_id = OLD.id;
END;""")

delete_admin_trigger = DDL("""
CREATE TRIGGER delete_admin
BEFORE DELETE ON ADMIN
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, 'Super admin cannot be deleted.')
    WHERE OLD.id = (SELECT id FROM ADMIN WHERE level = 1 LIMIT 1);
    DELETE from CONTACT WHERE admin_id = OLD.id;
    DELETE from GROUPS WHERE admin_id = OLD.id;
    DELETE from AUTHORIZED_SUPERVISOR_ACTION WHERE admin_id = OLD.id;
    UPDATE ACTION
    SET admin_id = (SELECT id FROM ADMIN WHERE level = 1 LIMIT 1)
    WHERE admin_id = OLD.id;
    UPDATE SMS
    SET admin_id = (SELECT id FROM ADMIN WHERE level = 1 LIMIT 1)
    WHERE admin_id = OLD.id;
    INSERT INTO COMMANDS(command, params) VALUES('DELETE_ADMIN', '{"email": "' || OLD.email || '"}');
END;""")

force_only_one_super_admin = DDL("""
CREATE TRIGGER only_one_super_admin
BEFORE INSERT ON ADMIN
FOR EACH ROW
WHEN NEW.level = 1
BEGIN
    SELECT RAISE(ABORT, 'There can be only one super admin.')
    WHERE EXISTS (SELECT 1
                  FROM ADMIN
                  WHERE level = 1);
END;""")

add_supervisor = DDL("""
CREATE TRIGGER add_supervisor
AFTER INSERT ON ADMIN
FOR EACH ROW
WHEN NEW.level = 2
BEGIN
    INSERT INTO COMMANDS(command, params)
    VALUES('ADD_ADMIN',
    '{
        "login": "' || NEW.login || '",
        "email": "' || NEW.email || '",
        "phone_number": "' || NEW.phone_number || '",
        "password": "' || NEW.password || '",
        "auth_backend": "' || NEW.auth_backend || '"
    }');
END;""")

update_supervisor_quota = DDL("""
CREATE TRIGGER update_supervisor_quota
AFTER UPDATE OF sms_quota ON ADMIN
FOR EACH ROW
WHEN OLD.sms_quota <> NEW.sms_quota AND OLD.level = 2 AND NEW.sms_quota NOT LIKE '!%%' AND OLD.sms_quota NOT LIKE '!%%'
BEGIN
    INSERT INTO COMMANDS(command, params)
    VALUES('UPDATE_QUOTA',
    '{
        "quota": "' || NEW.sms_quota || '",
        "email": "' || NEW.email || '"
    }');
END;""")

request_supervisor_quota = DDL("""
CREATE TRIGGER request_supervisor_quota
AFTER UPDATE OF sms_quota ON ADMIN
FOR EACH ROW
WHEN NEW.sms_quota LIKE '!%%'
BEGIN
    UPDATE ADMIN SET sms_quota = OLD.sms_quota WHERE id = NEW.id;
    INSERT INTO COMMANDS(command, params)
    VALUES('REQUEST_QUOTA',
    '{
        "new_quota": "' || NEW.sms_quota || '",
        "old_quota": "' || OLD.sms_quota || '",
        "name": "' || NEW.firstname || ' ' || NEW.name || '"
    }');
END;""")

event.listen(Group.__table__, 'after_create', delete_group_trigger)
event.listen(Contact.__table__, 'after_create', delete_contact_trigger)
event.listen(ContactGroup.__table__, 'after_create', delete_contact_group_trigger)
event.listen(AuthorizedGroupAction.__table__, 'after_create',
             delete_authorized_group_action_trigger)
event.listen(Action.__table__, 'after_create', delete_action_trigger)
event.listen(Action.__table__, 'after_create', update_action_trigger)
event.listen(Admin.__table__, 'after_create', delete_admin_trigger)
event.listen(Admin.__table__, 'after_create', force_only_one_super_admin)
event.listen(Admin.__table__, 'after_create', add_supervisor)
event.listen(Admin.__table__, 'after_create', update_supervisor_quota)
event.listen(Admin.__table__, 'after_create', request_supervisor_quota)
