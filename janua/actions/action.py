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

import operator
import re

from functools import wraps

import janua.utils.logger as jlogger

from janua import jdb, sms_queue, mail_queue, config
from janua.utils.utilities import get_subclasses
from janua.utils.mail import MailError, MailObj
from janua.utils.utilities import doctrim, extract_group_number_and_mail
from janua.utils.utilities import valid_prefix_number, get_role
from janua.utils.mail import valid_email
from janua.actions import ActionNotifyError, ActionError

log = jlogger.getLogger(__name__)

action_ref = {
    'id': 0,
    'list': [],
    'keyword_list': [],
}

# constants
TYPE_ACCEPTED = ['int', 'str', 'list', 'date', 'time', 'float', 'multilist']

class multilist(list):
    """Allow multiple value for an action argument"""
    pass

class date(str):
    """Define date type argument as string"""
    pass

class time(int):
    """Define time type argument as integer (timestamp)"""
    pass

class _ArgDict(dict):
    """To identify argument decorated function"""
    pass

def argument(required=True):
    """Decorator for action argument"""
    def wrap(func):
        if func.func_doc == None:
            raise SyntaxError(
                'documentation string for argument %s in %s is missing'
                % (func.func_name, func.__module__)
            )
        return _ArgDict({
            'name': func.func_name,
            'desc': doctrim(func.func_doc),
            'type': None,
            'value': None,
            'optional': not required,
            'arg_func': func
        })
    return wrap

def ret_value(ret):
    """Set return value of action argument"""
    return lambda: ret

def console_error(message):
    return False, message

def console_success(message):
    return True, message

def _console_context_args(func):
    """Decorator for processing action arguments from console interface"""
    def process_args(self, arguments):
        self.running_context = 'console'
        log.debug(
            'Console context: processing arguments of action %s',
            self.get_name()
        )
        for arg in self.get_arguments():
            if arg['name'] in arguments:
                if arg['type'] != 'multilist':
                    if arguments[arg['name']]:
                        val = arguments[arg['name']][0]
                    else:
                        val = arguments[arg['name']]
                else:
                    val = arguments[arg['name']]
                setattr(self, arg['name'], ret_value(val))
        return func(self)
    return process_args

def _sms_context_args(func):
    """Decorator for processing action arguments from sms interface"""
    def process_args(self, arguments, keyword):
        self.running_context = 'sms'
        if keyword == True:
            # return a list ala sys.argv
            setattr(self, 'keyword_arguments', arguments)
        elif len(arguments) > 0:
            log.debug(
                'Sms context: processing arguments of action %s',
                self.get_name()
            )
            for arg in arguments:
                try:
                    index = int(arg[0], 10)
                except ValueError:
                    raise ActionError('Unknown argument')
                else:
                    value = arg[1]
                    action_args = self.get_arguments()
                    if index >= 0 and index < len(action_args):
                        action_arg = action_args[index]
                        argtype = action_arg['type']
                        if argtype == 'int':
                            try:
                                value = int(value)
                            except ValueError:
                                raise ActionError(
                                    'Wrong value for argument %s'
                                    % action_arg['name']
                                )
                        elif argtype == 'float':
                            try:
                                value = float(value)
                            except ValueError:
                                raise ActionError(
                                    'Wrong value for argument %s'
                                    % action_arg['name']
                                )
                        elif argtype == 'multilist':
                            multival = []
                            for val in value.split(','):
                                try:
                                    ival = int(val)
                                except ValueError:
                                    raise ActionError(
                                        'Wrong value for argument %s'
                                        % action_arg['name']
                                    )
                                else:
                                    try:
                                        multival.append(
                                            action_arg['value'][ival]
                                        )
                                    except IndexError:
                                        raise ActionError(
                                            'Wrong value for argument %s'
                                            % action_arg['name']
                                        )
                            value = multival
                        elif argtype == 'list':
                            try:
                                value = action_arg['value'][int(value)]
                            except (ValueError, IndexError):
                                raise ActionError(
                                    'Wrong value for argument %s'
                                    % action_arg['name']
                                )
                        elif argtype == 'time':
                            try:
                                value = int(value)
                            except ValueError:
                                raise ActionError(
                                    'Wrong value for argument %s'
                                    % action_arg['name']
                                )

                        setattr(self, action_arg['name'], ret_value(value))

        return func(self)
    return process_args

class WebInit(object):
    def __init__(self, func, init_callback):
        self.func = func
        self.init_callback = init_callback

    def init(self, clsname, method):
        return self.init_callback(clsname, method)

def _web_context_args(func):
    """Decorator for processing action arguments from web interface"""
    def process_args(self, arguments, *args, **kwargs):
        log.debug(
            'Web context: processing arguments of action %s',
            self.get_name()
        )
        self.running_context = 'web'
        for arg in self.get_arguments():
            if arg['name'] not in arguments and arg['optional'] == False:
                raise ActionError('Action argument %s is required' % arg['name'])

            if arg['name'] in arguments:
                val = arguments[arg['name']]
                argtype = arg['type']
                if argtype == 'int':
                    try:
                        val = int(val)
                    except ValueError:
                        raise ActionError(
                            'Wrong value for argument %s'
                            % arg['name']
                        )
                elif argtype == 'float':
                    try:
                        val = float(val)
                    except ValueError:
                        raise ActionError(
                            'Wrong value for argument %s'
                            % arg['name']
                        )
                elif argtype == 'list':
                    if val not in arg['value']:
                        raise ActionError('Valid value for %s argument are %s' % (arg['name'], ','.join(arg['value'])))
                    val = str(val)
                elif argtype == 'multilist':
                    val = val.split(',')
                    for v in val:
                        if v not in arg['value']:
                            raise ActionError('Valid values for %s argument are %s' % (arg['name'], ','.join(arg['value'])))
                elif argtype == 'time':
                    try:
                        val = int(val)
                    except ValueError:
                        raise ActionError(
                            'Wrong value for argument %s'
                            % arg['name']
                        )
                setattr(self, arg['name'], ret_value(val))
        return func(self, *args, **kwargs)
    return process_args

class NotifyFlags(object):
    sms = 1 << 1
    mail = 1 << 2
    sender = 1 << 3
    contacts = 1 << 4
    admin = 1 << 5
    supervisors = 1 << 6
    manager = 1 << 7

class NotifyMethod(object):
    """
    Notification methods
    """

    def __init__(self, pool, action, flags):
        self.pool = pool
        self.action = action
        self.flags = flags

    def _check_notify_arg(self, arg):
        if self.action.running_context == 'sms' and not isinstance(arg, basestring):
            raise ActionNotifyError('argument is not a string type')
        if self.action.running_context == 'mail' and not isinstance(arg, MailObj):
            raise ActionNotifyError('argument is not a MailObj type')

    def sender(self, arg):
        """
        To notify sender which trigger action

        :param arg: message for sms, :class:`.MailObj` for mail
        """
        self._check_notify_arg(arg)
        self.pool.add(
            (self.flags|NotifyFlags.sender, arg)
        )

    def manager(self, arg):
        """
        To notify administrator which manage this action, available in SMS
        context only

        :param arg: message for sms, :class:`.MailObj` for mail
        """
        self._check_notify_arg(arg)
        if self.action.running_context == 'sms':
            self.pool.add(
                (self.flags|NotifyFlags.manager, arg)
            )
        else:
            raise ActionNotifyError('Not available in this context')

    def admin(self, arg):
        """
        To notify super administrator

        :param arg: message for sms, :class:`.MailObj` for mail
        """
        self._check_notify_arg(arg)
        self.pool.add(
            (self.flags|NotifyFlags.admin, arg)
        )

    def contacts(self, arg):
        """
        To notify contacts based on group membership of the sender, available
        in SMS context only

        :param arg: message for sms, :class:`.MailObj` for mail
        """
        self._check_notify_arg(arg)
        if self.action.running_context == 'sms':
            self.pool.add(
                (self.flags|NotifyFlags.contacts, arg)
            )
        else:
            raise ActionNotifyError('Not available in this context')

    def supervisors(self, arg):
        """
        To notify all supervisors

        :param arg: message for sms, :class:`.MailObj` for mail
        """
        self._check_notify_arg(arg)
        self.pool.add((self.flags|NotifyFlags.supervisors, arg))

class Notify(object):
    """
    Notify wrapper class
    """

    sms = None
    """sms notify method object (:class:`.NotifyMethod`)"""

    mail = None
    """mail notify method object (:class:`.NotifyMethod`)"""

    def __init__(self, action):
        self._pool = set()
        self.sms = NotifyMethod(self._pool, action, NotifyFlags.sms)
        self.mail = NotifyMethod(self._pool, action, NotifyFlags.mail)

    @property
    def pool(self):
        return self._pool

    def __getattr__(self, name):
        if name not in ['sms', 'mail']:
            raise ActionNotifyError(
                '%s is not a valid notify attribute'
                % name
            )

def available_action_list(include_keyword=True):
    """Available action objects as list
    @param include_keyword: include keyword action or not
    @return a list of action objects
    """
    slist = sorted(get_subclasses(Action), key=lambda action: action.get_id())
    if include_keyword == True:
        return slist
    else:
        return [action for action in slist if action.keyword == None]

def available_action_dict(include_keyword=True):
    """Available action objects as dictionary
    @param include_keyword: include keyword action or not
    @return a dictionary of action objects
    """
    clsdict = {}
    for cls in get_subclasses(Action):
        if include_keyword == False and cls.keyword != None:
            continue
        clsdict.update({cls.get_name(): cls})
    return clsdict

def get_custom_action_repr(context, filtered, authorized_actions):
    """Get custom action class information based on context
    @param context: action context
    @param filtered: is action should be filtered
    @param authorized_actions: only action in the list will be listed
    @return a dictionary containing action class information
    """
    dict_actions = {'totalaction': 0, 'totalcategory': 0,
                   'action': [], 'category': []}
    for action in available_action_list(include_keyword=False):
        action_category = action.category
        action_contexts = action.get_contexts()
        if action_category != '__INTERNAL__' and \
           context in action_contexts and \
           action.enabled:
            if filtered and (action.get_name() not in authorized_actions):
                continue
            dict_actions['totalaction'] += 1
            dict_actions['action'].append(action.get_class_info())
            if action_category not in dict_actions['category']:
                dict_actions['totalcategory'] += 1
                dict_actions['category'].append(action_category)
    return dict_actions

class _MetaAction(type):
    """Private meta class for action class."""

    def __new__(mcs, clsname, bases, dct):
        web_init = None
        conv_clsname = re.sub('([A-Z]{1}[a-z]{1})', r'_\1', clsname).lstrip('_').lower()

        for name, module in action_ref['list']:
            if name == conv_clsname:
                raise NameError(
                    'class %s is already defined in %s'
                    % (clsname, module)
                )
            if dct['__module__'] == module:
                raise SyntaxError(
                    'only one action per module are allowed. Remove %s from %s'
                    % (clsname, dct['__module__'])
                )

        action_ref['list'].append((conv_clsname, dct['__module__']))

        for keyword, module in action_ref['keyword_list']:
            if 'keyword' in dct and keyword == dct['keyword'].lower():
                raise NameError('keyword action %s is already defined '
                                'in %s' % (keyword, module))

        if 'keyword' in dct and dct['keyword'] != None:
            action_ref['keyword_list'].append((dct['keyword'].lower(),
                                       dct['__module__']))

        dct.update({'_arguments': []})
        parent_dict = bases[0].__dict__

        index = 0

        for k in sorted(dct.iterkeys()):
            if isinstance(dct[k], _ArgDict):
                arg = dct[k]
                func = arg['arg_func']
                ret = func(mcs)

                arg['type'] = type(ret).__name__
                if arg['type'] not in TYPE_ACCEPTED:
                    raise TypeError(
                        'Type %s as action argument is not allowed'
                        % arg['type']
                    )
                arg['value'] = ret

                # action arguments can't be overriden to avoid mistakes
                if parent_dict.has_key('_arguments'):
                    for parent_arg in parent_dict['_arguments']:
                        if arg['name'] in parent_arg['_name']:
                            raise NameError(
                                '%s argument in %s already exists in %s'
                                % (arg['name'], clsname, bases[0].__name__)
                            )

                dct['_arguments'].append({
                    'id': index,
                    'name': arg['name'],
                    'desc': arg['desc'],
                    'type': arg['type'],
                    'value': arg['value'],
                    'optional': arg['optional']
                })
                index += 1
                dct[k] = lambda x: None

            if k in ['sms', 'console', 'web', 'unittest']:
                func = dct[k]
                context = k
                if context == 'console':
                    dct['call_console_context'] = _console_context_args(func)
                elif context == 'sms':
                    dct['call_sms_context'] = _sms_context_args(func)
                elif context == 'web':
                    if isinstance(func, WebInit):
                        dct['call_web_context'] = _web_context_args(func.func)
                        web_init = func
                    else:
                        raise SyntaxError('Missing url decorator for web method in class %s' % dct['__module__'])
                if '_contexts' not in dct:
                    dct['_contexts'] = []
                dct['_contexts'].append(context)

        # inherit argument from parent
        if parent_dict.has_key('_arguments'):
            dct['_arguments'] = parent_dict['_arguments'] + dct['_arguments']

        if web_init:
            method = 'GET'
            if dct['_arguments']:
                method = 'POST'
            web_init.init(conv_clsname, method)

        if clsname != 'Action':
            # sanity checks
            if '_contexts' not in dct or (len(dct['_contexts']) == 1 and \
                                          'unittest' in dct['_contexts']):
                raise SyntaxError(
                    'action class in %s should contain at least one of these methods: sms, web, console'
                    % dct['__module__']
                )

            if 'keyword' in dct and dct['keyword'] != None:
                if 'sms' not in dct['_contexts']:
                    raise SyntaxError(
                        'keyword action class in %s has no sms method'
                        % dct['__module__']
                    )
            elif 'filtered' in dct and dct['filtered'] == False:
                dct['filtered'] = True

            if 'category' not in dct or dct['category'] == None:
                raise AttributeError(
                    'category attribute for action class in %s is missing'
                    % dct['__module__']
                )

            if '__doc__' not in dct:
                raise SyntaxError(
                    'documentation string for action class in %s is missing'
                    % dct['__module__']
                )

            if 'keyword' in dct and dct['keyword'] != None:
                dct['keyword'] = dct['keyword'].lower()

            dct.update({
                '_name': conv_clsname,
                '_desc': doctrim(dct['__doc__']),
                '_id': action_ref['id']
            })
            action_ref['id'] += 1

        return super(_MetaAction, mcs).__new__(mcs, clsname, bases, dct)

class Action(object):
    """
    Action parent class, all action class must inherit from it
    """

    __metaclass__ = _MetaAction
    """the fun part"""

    category = None
    """
    Category to sort actions

    .. note::
       category **__INTERNAL__** is for internal use
    """

    dangerous = False
    """
    Action is dangerous ? (Janua Client)
    """

    phone_number = None
    """
    phone number to determine which sender trigger action (**sms context only**)
    """

    email = None
    """
    email of administrator who trigger action
    """

    keyword = None
    """
    sms keyword which trigger action

    .. note::
       an action triggered with sms keyword don't require authentication.

       If filtered attribute set to:
        * True: only phone numbers in authorized group are allowed to trigger action
        * False: anyone can trigger action
    """

    keyword_arguments = []
    """
    sms keyword arguments, typically all words behind keyword are considered as
    arguments
    """

    enabled = True
    """
    Flag to enable or disable action
    """

    filtered = True
    """
    For keyword
    """

    notify = None
    """
    notify object
    """

    admin = None
    """
    Admin database object which managed this action
    """

    _contexts = []
    """List of contexts"""

    _arguments = None
    """Action arguments"""

    _name = None
    """Action name"""

    _desc = None
    """Action description, take from class docstring"""

    _id = None
    """Action unique id"""

    _running_context = None
    """In which context action run"""

    def __new__(cls):
        """Don't allow instance of disabled action"""
        if cls.enabled:
            return super(Action, cls).__new__(cls)
        raise ActionError('Action was disabled')

    def __init__(self):
        """"""
        self.notify = Notify(self)
        if self.category == '__INTERNAL__':
            self.admin = jdb.admin.get_super_admin()
        else:
            action = jdb.action.get_by_janua_id(self.get_id())
            if not action:
                raise ActionError('Cannot associate admin to action')
            self.admin = jdb.admin.get_by_id(action.admin_id)
            if not self.admin:
                raise ActionError('No action supervisor was found')

    @classmethod
    def get_name(cls):
        """Get class name"""
        return cls._name

    @classmethod
    def get_desc(cls):
        """Get formatted description from class documentation string"""
        return cls._desc

    @classmethod
    def get_arguments(cls):
        """Get action arguments"""
        return cls._arguments

    @classmethod
    def get_contexts(cls):
        """Get action contexts"""
        return cls._contexts

    @classmethod
    def get_class_info(cls):
        """Get action class information"""
        return {
            'name': cls._name,
            'category': cls.category,
            'desc': cls._desc,
            'id': cls._id,
            'args': cls._arguments,
            'dangerous': cls.dangerous
        }

    @classmethod
    def get_id(cls):
        """Get action id"""
        return cls._id

    @classmethod
    def get_module(cls):
        """Get module namespace"""
        return cls.__module__

    @property
    def running_context(self):
        """Get running context"""
        return self._running_context
    @running_context.setter
    def running_context(self, value):
        self._running_context = value

    def call_sms_context(self, arguments, keyword):
        """Call child sms method"""
        raise NotImplementedError('Not supported')

    def call_console_context(self, arguments):
        """Call child console method"""
        raise NotImplementedError('Not supported')

    def call_web_context(self, arguments):
        """Call child web method"""
        raise NotImplementedError('Not supported')

    def send_sms(self, message=None, to=None, filtered=True):
        """
        Send SMS

        :param message: SMS message
        :param to: string containing phone number and/or group name separated by commas
        :param filtered: authorized to send only to managed contacts or send to anyone
        :returns: tuple (success, message) where success is a boolean to indicate success or error
        """
        if not message or not to:
            return False, 'No recipients and/or message'

        from_number = self.phone_number
        if not from_number:
            return False, 'Couldn\'t retrieve your phone number'

        if self.running_context == 'web':
            admin = jdb.admin.get_by_phone(self.phone_number)
            admin_id = admin.id
            if filtered == True:
                filtered = admin.recipient_filter
        else:
            admin_id = self.admin.id
            if filtered == True:
                filtered = self.admin.recipient_filter

        admins = [adm.phone_number for adm in jdb.admin.get_all()]

        groups, numbers, _ = extract_group_number_and_mail(to)

        dbgroups = jdb.group.get_by_admin_phone(from_number)
        dbcontacts = jdb.contact.get_by_admin_phone(from_number)
        group_ids = set()

        if dbcontacts == [] and dbgroups == [] and filtered:
            return False, 'No recipient was found in database for your account'

        list_groups = [g.name for g in dbgroups]
        for group in groups:
            if group not in list_groups and group != 'all':
                return False, 'Group %s is invalid' % group
            else:
                try:
                    group_match = filter(lambda x: x.name == group, dbgroups)[0]
                except (IndexError, ValueError):
                    continue
                group_ids.add(group_match.id)

        if 'all' in groups:
            contacts = set(jdb.contact.get_by_admin_phone(self.phone_number))
        else:
            contacts = set()
            list_numbers = [contact.phone_number for contact in dbcontacts]
            for number in numbers:
                if not valid_prefix_number(number, config.sms.prefix_filter):
                    return False, 'Number %s doesn\'t have a valid prefix' % number

                if filtered and number not in list_numbers:
                    return False, 'Number %s is invalid' % number

                if number in admins:
                    contact = jdb.admin.get_by_phone(number)
                else:
                    try:
                        contact = filter(lambda x: x.phone_number == number, dbcontacts)[0]
                    except (IndexError, ValueError):
                        continue

                if contact:
                    contacts.add(contact)
                elif not filtered:
                    contacts.add(number)

            if group_ids:
                contacts.update(jdb.contact.get_by_group_id(group_ids))

        for contact in contacts:
            if hasattr(contact, 'phone_number'):
                sms_queue.put((message, contact.phone_number, admin_id))
            else:
                sms_queue.put((message, contact, admin_id))

        if contacts:
            return True, 'SMS message has been queued'

        return False, 'No recipients was found in database to send SMS to %s' % to

    def send_email(self, subject=None, message=None, to=None, template=None, template_args={}, filtered=True):
        """
        Send mail

        :param subject: mail subject
        :param message: mail body
        :param to: string containing phone number, group name or mail separated by commas
        :param template: mail template to use
        :param template_args: mail template arguments
        :param filtered: authorized to send only to managed contacts or send to anyone
        :returns: tuple (success, message) where success is a boolean to indicate success or error
        """
        from_number = self.phone_number

        if not from_number:
            return False, 'Couldn\'t retrieve your phone number'

        if self.running_context == 'web':
            admin = jdb.admin.get_by_phone(self.phone_number)
            admin_email = admin.email
            if filtered == True:
                filtered = admin.recipient_filter
        else:
            admin_email = self.admin.email
            if filtered == True:
                filtered = self.admin.recipient_filter

        admins = [adm.email for adm in jdb.admin.get_all()]

        try:
            groups, numbers, mails = extract_group_number_and_mail(to)
        except AttributeError, err:
            return False, 'There is no recipients'

        dbgroups = jdb.group.get_by_admin_phone(from_number)
        dbcontacts = jdb.contact.get_by_admin_phone(from_number)
        group_ids = set()

        if dbcontacts == [] and dbgroups == [] and filtered:
            return False, 'No recipient was found in database for your account'

        list_groups = [g.name for g in dbgroups]
        for group in groups:
            if group not in list_groups and group != 'all':
                return False, 'Group %s is invalid' % group
            else:
                try:
                    group_match = filter(lambda x: x.name == group, dbgroups)[0]
                except (IndexError, ValueError):
                    continue
                group_ids.add(group_match.id)

        if 'all' in groups:
            contacts = set(jdb.contact.get_by_admin_phone(from_number))
        else:
            list_mails = [contact.email for contact in dbcontacts]
            list_numbers = [contact.phone_number for contact in dbcontacts]
            contacts = set()
            for number in numbers:
                if not valid_prefix_number(number, config.sms.prefix_filter):
                    return False, 'Number %s doesn\'t have a valid prefix' % number

                if number not in list_numbers:
                    return False, 'Number %s is not in your contact list' % number

                if number in admins:
                    contact = jdb.admin.get_by_phone(number)
                else:
                    try:
                        contact = filter(lambda x: x.phone_number == number, dbcontacts)[0]
                    except (IndexError, ValueError):
                        continue

                if contact:
                    contacts.add(contact)

            for mail in mails:
                if not valid_email(mail):
                    return False, 'Mail %s doesn\'t have a valid format' % mail

                if filtered and mail not in list_mails:
                    return False, 'Mail %s is invalid' % mail

                if mail in admins:
                    contact = jdb.admin.get_by_mail(mail)
                else:
                    try:
                        contact = filter(lambda x: x.email == mail, dbcontacts)[0]
                    except (IndexError, ValueError):
                        continue

                if contact:
                    contacts.add(contact)
                elif not filtered:
                    contacts.add(mail)

            if group_ids:
                contacts.update(jdb.contact.get_by_group_id(group_ids))

        try:
            mailobj = MailObj()
            if admin_email:
                mailobj.reply_to = admin_email

            if template:
                mailobj.template = template
                mailobj.template_args = template_args
            else:
                mailobj.message = message
                mailobj.subject = subject
        except MailError, err:
            return False, err[0]

        log.debug('process contact')

        for contact in contacts:
            if hasattr(contact, 'email'):
                mailobj.to = contact.email
            else:
                mailobj.to = contact
            mail_queue.put(mailobj)

        if contacts:
            return True, 'Mail has been queued'

        return False, 'No recipients was found to send email'

    def process_notify(self):
        """
        Process notify message pool
        """
        flags = NotifyFlags

        for notify_args in self.notify.pool:
            phone_numbers = set()
            mail_to = set()
            notify_flags, arg = notify_args
            db_action = jdb.action.get_by_janua_id(self.get_id())

            if self.running_context == 'sms':
                if not db_action and self.get_id() > 0:
                    return 'No action corresponding to janua_id %d was found in database' % self.get_id()

            if notify_flags & flags.sender:
                log.debug('Notify sender')
                phone_numbers.add(self.phone_number)
                if self.email:
                    mail_to.add(self.email)
            elif (notify_flags & flags.manager) and db_action:
                log.debug('Notify manager')
                entry = jdb.admin.get_by_id(db_action.admin_id)
                phone_numbers.add(entry.phone_number)
                mail_to.add(entry.email)
            elif notify_flags & flags.admin:
                log.debug('Notify admin')
                entry = jdb.admin.get_super_admin()
                phone_numbers.add(entry.phone_number)
                mail_to.add(entry.email)
            elif notify_flags & flags.supervisors:
                log.debug('Notify supervisors')
                for entry in jdb.admin.get_all():
                    if get_role(entry) == 'supervisor':
                        phone_numbers.add(entry.phone_number)
                        mail_to.add(entry.email)
            elif (notify_flags & flags.contacts) and db_action:
                log.debug('Notify contacts')
                contacts = jdb.contact.get_by_action_id(db_action.id)
                try:
                    contact = filter(lambda x: x.phone_number == self.phone_number, contacts)[0]
                except (IndexError, ValueError):
                    return 'No contact associated with %s' % self.phone_number

                group_ids = [group.id for group in jdb.group.get_by_contact_id(contact.id)]
                contact_ids = [cn.contact_id for cn in jdb.contact_notify.get_by_action_id(db_action.id) if cn.group_id in group_ids]
                for contact_id in contact_ids:
                    if contact_id != contact.id:
                        contact_notify = jdb.contact.get_by_id(contact_id)
                        phone_numbers.add(contact_notify.phone_number)
                        mail_to.add(contact_notify.email)

            if notify_flags & flags.sms:
                message = arg
                data = None
                if message:
                    data = message
                    log.info('Action notify: %s' % message)
                if data:
                    success, message = self.send_sms(data, ','.join(phone_numbers), False)
                    if not success:
                        return message
                else:
                    return 'SMS message is empty'

            if notify_flags & flags.mail:
                if isinstance(arg, MailObj):
                    return 'Mail notify argument is not a MailObj instance'

                kwargs = {
                    'subject': arg.subject,
                    'message': arg.message,
                    'to': ','.join(mail_to),
                    'template': arg.template,
                    'template_args': arg.template_args,
                    'filtered': False
                }
                success, message = self.send_email(**kwargs)
                if not success:
                    return message


def update_action_table():
    db_actions = jdb.action.get_all()
    db_actions_module = [action.module for action in db_actions]
    db_actions_id = [action.janua_id for action in db_actions]
    available_actions = [
        action
        for action in available_action_list()
        if action.category != '__INTERNAL__' and 'sms' in action.get_contexts()
    ]
    actions_module = []
    roll_actions = []
    add_action = []
    max_id = 0

    for action in available_actions:
        if action.get_module() not in db_actions_module:
            add_action.append(action)
        else:
            index = db_actions_module.index(action.get_module())
            db_action = db_actions[index]
            if db_action.janua_id != action.get_id():
                roll_actions.append(
                    (
                        action.get_module(),
                        action.get_id(),
                        db_action.janua_id,
                        action
                    )
                )
                if action.get_id() > max_id:
                    max_id = action.get_id()
            else:
                db_action.name = action.get_name()
                db_action.description = action.get_desc()
                db_action.authentication = True if action.keyword == None else False
                db_action.enabled = action.enabled
                if jdb.update_entry(db_action):
                    actions_module.append(action.get_module())
                else:
                    log.error('Can not update action %s', action.get_module())

    if not db_actions_id:
        reverse = False
    else:
        reverse = False if max(db_actions_id) > max_id else True
    roll_actions.sort(key=operator.itemgetter(1), reverse=reverse)

    if reverse == False:
        roll_module = [action[0] for action in roll_actions]
        for action in db_actions:
            if action.module not in actions_module and \
               action.module not in roll_module:
                if jdb.del_entry(action) == False:
                    log.error('Can not delete action %s', action.module)

    for module in roll_actions:
        index = db_actions_id.index(module[2])
        db_action = db_actions[index]
        action = module[3]
        db_action.name = action.get_name()
        db_action.description = action.get_desc()
        db_action.authentication = True if action.keyword == None else False
        db_action.enabled = action.enabled
        db_action.janua_id = module[1]
        if jdb.update_entry(db_action):
            actions_module.append(action.get_module())
        else:
            log.error('Can not update action %s', action.get_module())

    for action in add_action:
        authentication = True if action.keyword == None else False
        if jdb.action.add(action.get_name(),
                                action.get_module(),
                                action.get_desc(),
                                authentication,
                                action.enabled,
                                action.get_id()) == False:
            log.error('Can not add action %s', action.get_module())
        else:
            actions_module.append(action.get_module())
