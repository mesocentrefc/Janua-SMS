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

import argparse
import sys

class ArgParse(object):
    """
    Argument parser object
    """
    def __init__(self, *args, **kwargs):
        """
        Parser initialization
        """
        self.parser = argparse.ArgumentParser(*args, **kwargs)
        self.section_subparser = None
        self.section_parser = None
        self.callback = {}
        self.sections = []
        self.command_parser = self.parser
        
    def add_argument(self, *args, **kwargs):
        """
        Add argument to parse
        """
        self.parser.add_argument(*args, **kwargs)

    def add_section(self, *args, **kwargs):
        """
        Add a section or subparser
        """
        if 'dest' in kwargs:
            self.sections.append(kwargs['dest'])

        self.subparser = self.parser.add_subparsers(*args, **kwargs)

    def add_section_argument(self, *args, **kwargs):
        """
        Add a section argument to parse
        """
        self.section_parser.add_argument(*args, **kwargs)
        
    def add_section_command(self, name, title=None, description=None, help=None, subcommand=False, callback=None):
        """
        Add a section callback command

        :param name: command name
        :param title: command title
        :param description: command description
        :param help: command help
        :param subcommand: is command has subcommand
        :param callback: command callback function
        """
        if subcommand:
            self.section_parser = self.subparser.add_parser(name)
            self.section_subparser = self.section_parser.add_subparsers(title=title, description=description, help=help, dest=name)
        else:
            self.section_parser = self.subparser.add_parser(name, description=description)
        if callback:
            self.callback.update({name: callback})

    def add_section_subcommand(self, *args, **kwargs):
        """
        Add a section subcommand
        """
        self.section_parser = self.section_subparser.add_parser(*args, **kwargs)

    def add_section_subcommand_arg(self, *args, **kwargs):
        """
        Add a section subcommand argument
        """
        self.section_parser.add_argument(*args, **kwargs)
    
    def parse_argument(self):
        """
        Parse command line arguments and display help
        """
        if len(sys.argv[1:]) > 0:
            nsarg = self.parser.parse_args(sys.argv[1:])
            args = vars(nsarg)
            for section in self.sections:
                if section in args and args[section]:
                    cb = self.callback[args[section]]
                    if cb:
                        cb(args)
        else:
            self.parser.print_usage()
