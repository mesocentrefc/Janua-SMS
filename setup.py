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
import site
import stat
import sys

try:
    from setuptools import setup
    from setuptools.command.install import install
except ImportError, err:
    from distutils.core import setup
    from distutils.command.install import install

from string import Template

janua_root_install = '/opt/janua'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def find_version(file_paths):
    version_file = read(file_paths)
    version_match = re.search(r"^__VERSION__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')

def recursive_copy_data_files(directory, dest=None):
    return [
        (
            os.path.join(janua_root_install, templates[0])
            if not dest else os.path.join(
                janua_root_install, dest, templates[0].replace(directory, '')
            ),
            [os.path.join(templates[0], file) for file in templates[2]]
        ) for templates in os.walk(directory) if templates[2]]

janua_packages = [
    'janua',
    'janua.actions',
    'janua.activity',
    'janua.db',
    'janua.sms',
    'janua.utils',
    'janua.utils.android',
    'janua.utils.sms',
    'janua.ws',
    'janua.ws.api',
    'janua.auth',
    'janua.commands'
]

data_files = [
    ('%s/custom' % janua_root_install, ['custom/__init__.py']),
    ('%s/custom/actions' % janua_root_install, ['custom/actions/__init__.py']),
    ('%s/custom/lib' % janua_root_install, ['custom/lib/__init__.py']),
    ('%s/custom/auth' % janua_root_install, ['custom/auth/__init__.py']),
    ('%s/custom/engine' % janua_root_install, ['custom/engine/__init__.py']),
    ('%s/conf' % janua_root_install, ['']),
    ('%s/bin' % janua_root_install, ['']),
    ('/etc/init.d', ['scripts/init.d/janua'])
]

data_files += recursive_copy_data_files('mail_template')
data_files += recursive_copy_data_files('janua-web/build/production/JanuaWeb/', 'janua-web')
data_files += recursive_copy_data_files('packages')

setup(
    name = 'Janua-SMS',
    version = find_version('janua/utils/version.py'),
    author = 'Cédric Clerget - HPC Center of Franche-Comté University',
    author_email = 'cedric.clerget@univ-fcomte.fr',
    entry_points = {
        'console_scripts': [
            'janua = janua.main:run'
        ]
    },
    description = """An active SMS gateway""",
    install_requires = ['configobj>=4.7.2',
                        'Flask>=0.11.0',
                        'Flask-Restless==0.17.0',
                        'argparse>=1.2.1',
                        'cherrypy>=3.8.0',
                        'sqlalchemy==0.9.8',
                        'pyserial',
                        'mailer',
                        'paste',
                        'pysqlite',
                        'mailem',
                        'python-ldap'],
    license = 'GPLv2',
    keywords = 'sms active gateway server remote administration automation',
    url = 'http://github.com/mesocentrefc/Janua-SMS',
    packages = janua_packages,
    data_files = data_files,
    long_description = read('README'),
    platforms = 'Linux',
    provides = janua_packages,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Environment :: No Input/Output (Daemon)',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Topic :: Communications :: Telephony',
        'Topic :: Home Automation',
        'Topic :: System :: Monitoring'
    ]
)
