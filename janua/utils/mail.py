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
import re
from socket import getdefaulttimeout
import smtplib

from string import Template as STemplate

from mailem.connection import SMTPConnection
from mailem import Message, Postman
from mailem.template import Template
from mailem.template.renderer import IRenderer

class UnicodePythonTemplateRenderer(IRenderer):
    """ Simple Python Template renderer.

        Supported substitutions:

        * PythonTemplateRenderer('$what')(what=1)  #-> '1'
        * PythonTemplateRenderer('${what}')(what=1)  #-> '1'
        * PythonTemplateRenderer('$$what')(what=1)  #-> '$what'
    """

    def __init__(self, template):
        self.template = STemplate(unicode(template, 'utf-8'))

    def __call__(self, values):
        return self.template.substitute(values)


class MailError(Exception):
    """Mail error exception"""
    pass

class ESMTPConnection(SMTPConnection):
    def __init__(self, host, port, username, password, local_hostname=None, ssl=False, tls=False, timeout=getdefaulttimeout()):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.local_hostname = local_hostname
        self.ssl = ssl
        self.tls = tls
        self.timeout = timeout

        self.client = None

    def connect(self):
        # Init
        s = (smtplib.SMTP_SSL
             if self.ssl else
             smtplib.SMTP)(self.host, self.port, self.local_hostname, timeout=self.timeout)

        # Handshake
        if self.tls:
            s.starttls()

        if self.username and self.password:
            s.login(self.username, self.password)

        # Finish
        self.client = s

class MailObj(object):
    """
    Mail object which are passed to mail queue (see :class:`janua.utils.sqlite_queue.PersistentSqliteQueue`).

    .. note::
       If template attribute is defined, message and subject will be ignored

    **Example to send an email:**

    .. code-block:: python

       from janua import mail_queue
       from janua.utils.mail import MailObj, MailError
       from janua.utils.logger import getLogger

       log = getLogger(__name__)

       try:
           mailobj = MailObj()
           mailobj.message = "Where are you ?"
           mailobj.subject = "John"
           mailobj.to = "john.doe@nothing.here"
           mailobj.reply_to = "admin@nothing.here"
           mailobj.bcc = ["admin@nothing.here"]
       except MailError, err:
           log.error('Cannot instanciate mail object')

       mail_queue.put(mailobj)
    """
    def __init__(self):
        self._message = None
        self._subject = None
        self._to = []
        self._template = None
        self._template_args = {}
        self._reply_to = None
        self._bcc = None

    @property
    def message(self):
        """Mail body"""
        return self._message
    @message.setter
    def message(self, value):
        if not isinstance(value, basestring):
            raise MailError('Message argument must be a string')
        self._message = value

    @property
    def subject(self):
        """Mail subject"""
        return self._subject
    @subject.setter
    def subject(self, value):
        if not isinstance(value, basestring):
            raise MailError('Subject argument must be a string')
        self._subject = value

    @property
    def to(self):
        """Mail recipients"""
        return self._to
    @to.setter
    def to(self, value):
        if not isinstance(value, (basestring, list)):
            raise MailError('To argument must be a string or a list')
        self._to = value

    @property
    def template(self):
        """Mail template"""
        return self._template
    @template.setter
    def template(self, value):
        if not isinstance(value, basestring):
            raise MailError('Template argument must be a string')
        self._template = value

    @property
    def template_args(self):
        """Mail template arguements"""
        return self._template_args
    @template_args.setter
    def template_args(self, value):
        if not isinstance(value, dict):
            raise MailError('Template_args argument must be a dictionary')
        self._template_args = value

    @property
    def reply_to(self):
        """Mail reply to recipient"""
        return self._reply_to
    @reply_to.setter
    def reply_to(self, value):
        if not isinstance(value, basestring):
            raise MailError('Reply_to argument must be a string')
        self._reply_to = value

    @property
    def bcc(self):
        """Mail blind carbon copy"""
        return self._bcc
    @bcc.setter
    def bcc(self, value):
        if not isinstance(value, list):
            raise MailError('Bcc argument must be a list')
        self._bcc = value

class JanuaMailer():
    def __init__(self, config, januapath):
        self.config = config
        self.postman = None
        self.januapath = januapath

        if self.config.enable:
            connection = ESMTPConnection(
                config.smtp_host,
                config.smtp_port,
                config.smtp_username,
                config.smtp_password,
                local_hostname=None,
                ssl=config.smtp_ssl,
                tls=config.smtp_tls,
                timeout=config.smtp_timeout
            )
            self.postman = Postman(config.mail_from, connection)

    def get_template(self, name):
        path = os.path.join(
            self.januapath,
            'mail_template',
            self.config.mail_language.upper(),
            name
        )
        if not os.path.exists(path):
            raise MailError('Template %s not found' % name)

        template = Template.from_directory(
            path,
            subject_name='subject.txt',
            text_name='body.txt',
            html_name='body.html'
        )
        template.set_renderer(UnicodePythonTemplateRenderer)
        return template

    def sendmail(self, mailobj):
        if not isinstance(mailobj, MailObj):
            raise MailError('argument must be MailObj')

        if not self.config.enable:
            raise MailError('Mail option has been disabled, dropping mail ...')

        subject = mailobj.subject
        message = mailobj.message
        if isinstance(mailobj.to, list):
            to = mailobj.to
        else:
            to = [mailobj.to]
        template = mailobj.template
        template_args = mailobj.template_args
        reply_to = mailobj.reply_to
        bcc = mailobj.bcc

        if self.postman:
            if template:
                tmpl = self.get_template(template)
                msg = tmpl(to, template_args, reply_to=reply_to, bcc=bcc)
            else:
                msg = Message(to, subject, text=message, reply_to=reply_to, bcc=bcc)
            if msg:
                try:
                    with self.postman.connect() as c:
                        c.sendmail(msg)
                except Exception, err:
                    raise MailError(err)
                return True
        return False

def valid_email(address):
    """
    Check validity of email address

    :param address: mail address to validate
    :returns: True if valid, False otherwise
    """
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(pattern, address)
