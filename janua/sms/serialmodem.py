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
import os
import time
import threading

import janua.utils.logger as jlogger

from janua.sms.engine import SMSEngine
from janua.sms import SMSError, ModemError
from janua.utils.sms import SmsDeliver, SmsSubmit
from janua.utils.sms.atserial import ATSerial, BYTESIZE, PARITY, STOPBITS
from janua.utils.sms.atserial import isSMSUnsolicited, isFinalResponseError
from janua.utils.sms.atserial import isFinalResponseSuccess
from janua.utils.sms.atserial import SerialException

from operator import itemgetter

log = jlogger.getLogger(__name__)

config_spec = """
#
# serial modem section
#
[serial]
port = force_list(default='/dev/ttyACM0')    ; device name or port number number
baud = option(50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000, 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 400000, default=115200)    ; baud rate
bytesize = option(5, 6, 7, 8, default=8)    ; number of data bits. Possible values: 5, 6 ,7 ,8
parity = option('none', 'even', 'odd', 'mark', 'space', default='none')    ; parity checking. Possible values: none, even, odd, mark, space
stopbits = option(1, 1.5, 2, default=1)    ; number of stop bits. Possible values: 1, 1.5, 2
xonxoff = boolean(default=False)    ; software flow control
rtscts = boolean(default=True)    ; hardware RTS/CTS flow control
dsrdtr = boolean(default=False)    ; hardware DSR/DTR flow control
timeout = integer(default=1)    ; read timeout value in second
status_report = boolean(default=False)
"""

class SerialSMS(SMSEngine):
    """
    Serial modem SMS interface
    """
    name = 'serial'
    config_spec = config_spec

    def __init__(self, config):
        """
        Initialize stuff

        :param config: global configuration object
        """
        self.messagemutex = threading.Lock()
        self.readmutex = threading.Lock()

        self.port = config.serial.port
        self.baud = int(config.serial.baud)
        self.timeout = config.serial.timeout
        self.config = config
        self.connected = False

        self.serial_args = {
            'bytesize': BYTESIZE[config.serial.bytesize],
            'parity': PARITY[config.serial.parity],
            'stopbits': STOPBITS[config.serial.stopbits],
            'xonxoff': config.serial.xonxoff,
            'rtscts': config.serial.rtscts,
            'dsrdtr': config.serial.dsrdtr
        }

        self.messages = []
        self.concat_message = {}
        self.csca = None

        try:
            for port in self.port:
                if os.path.exists(port):
                    self.serial = ATSerial(port, self.baud, timeout=self.timeout, **self.serial_args)
        except (SerialException, ValueError, OSError), msg:
            raise ModemError(msg)

        if not hasattr(self, 'serial'):
            raise ModemError('No modem found')

        self._init_modem()

    def send_init_at_command(self, atcommand):
        try:
            err, resp = self.serial.at_init_command(atcommand)
        except SerialException, msg:
            raise ModemError(msg)
        if err:
            raise SMSError('AT%s failed by responding %s' % (atcommand, resp[-1]))

    def _init_modem(self):
        """
        Initialize modem
        """
        # some serial terminal initialization
        self.send_init_at_command('E0Q0V1')
        # modem not respond to phone call
        self.send_init_at_command('S0=0')
        # more readable result code
        self.send_init_at_command('+CMEE=1')

        # Set full phone functionality
        atcommand = '+CFUN?'
        try:
            err, resp = self.serial.at_init_command(atcommand)
        except SerialException, msg:
            raise ModemError(msg)
        if err:
            raise SMSError('AT%s failed by responding %s' % (atcommand, resp[-1]))
        else:
            if '+CFUN:' in resp[0]:
                result = resp[0][resp[0].find(' ') + 1:]
                if result == '0':
                    try:
                        err, resp = self.serial.at_init_command('+CFUN=1')
                        time.sleep(2)
                    except SerialException, msg:
                        raise ModemError(msg)
            else:
                raise SMSError('AT%s failed by responding %s' % (atcommand, resp[0]))

        # set pin code
        atcommand = '+CPIN?'
        try:
            err, resp = self.serial.at_init_command(atcommand)
        except SerialException, msg:
            raise ModemError(msg)
        if err:
            raise SMSError('AT%s failed by responding %s' % (atcommand, resp[-1]))
        else:
            if '+CPIN:' in resp[0]:
                result = resp[0][resp[0].find(' ') + 1:]
                if result == 'READY':
                    pass
                elif result == 'SIM PIN':
                    atcommand = '+CPIN="%s"' % self.config.sms.pin_code
                    try:
                        err, resp = self.serial.at_init_command(atcommand)
                        time.sleep(2)
                        if err:
                            raise SMSError('Wrong SIM PIN code: %s' % err)
                    except SerialException, msg:
                        raise ModemError(msg)
                else:
                    raise SMSError('SIM present ? because AT%s returned %s' % (atcommand, resp[0]))
            else:
                raise SMSError('AT%s failed by responding %s' % (atcommand, resp[0]))

        # modem network registration
        self.send_init_at_command('+COPS=0')
        # Set SMS PDU mode
        self.send_init_at_command('+CMGF=0')
        # Set GSM character set
        self.send_init_at_command('+CSCS="GSM"')

        # read service center address
        command_tries = 0
        while True:
            atcommand = '+CSCA?'
            try:
                err, resp = self.serial.at_init_command(atcommand)
            except SerialException, msg:
                raise ModemError(msg)
            if err:
                time.sleep(1)
                command_tries += 1
            else:
                response = resp[0]
                if '+CSCA:' in response:
                    self.csca = response.split('"')[1]
                    break
                else:
                    time.sleep(1)
                    command_tries += 1

            if command_tries == 5:
                raise SMSError('Failed to read the service center address')

        # set SMS status report
        if self.config.serial.status_report:
            self.send_init_at_command('+CNMI=1,2,2,1,0')
        else:
            self.send_init_at_command('+CNMI=1,2,2,0,0')

    def reconnect(self, event):
        """
        Endless loop to reconnect to serial modem

        :param event: thread event to interrupt loop
        """
        del self.serial
        while not event.isSet():
            for port in self.port:
                if os.path.exists(port):
                    log.info('Trying to establish communication with modem')
                    try:
                        self.serial = ATSerial(port, self.baud, timeout=self.timeout, **self.serial_args)
                        return
                    except (OSError, SerialException), err:
                        time.sleep(5)
                else:
                    time.sleep(1)

    def send(self, message, to):
        """
        Send SMS from a modem device

        :param message: message to send
        :param to: a phone number or all string to send to all contact numbers
        :returns: a tuple with reference which identify message and number of
                  slices of SMS sent (multi-part) or tuple of None if not supported
        """
        sms = SmsSubmit(to, message)
        sms.csca = self.csca
        sms.request_status = True
        ref_id = None
        slices = 0
        for pdu in sms.to_pdu():
            try:
                err, responses = self.serial.at_command_sms(pdu.pdu, pdu.length)
                slices += 1
            except SerialException, msg:
                del sms
                raise ModemError(msg)
            if err:
                del sms
                raise SMSError('AT sms command failed with response %s' % responses[-1])

            for response in responses:
                if not ref_id and '+CMGS:' in response:
                    ref_id = int(response.split(' ')[1])

        del sms
        return (ref_id, slices)

    def read_status_report(self, sms):
        if 'ref' not in sms:
            del sms
            return False
        else:
            ref = sms['ref']

        if 'number' not in sms:
            del sms
            return False

        delivered = False
        if sms['number'] == 'SR-OK':
            delivered = True

        self.messagemutex.acquire()
        self.messages.append({
            'body': sms['text'],
            'date': sms['date'],
            'address': sms['sr']['recipient'],
            'status': {'delivered': delivered, 'ref': ref},
        })
        self.messagemutex.release()

        del sms
        return True

    def read_sms(self, line):
        sms = SmsDeliver(line).data
        if 'sr' in sms and sms['sr'] != None:
            ret = self.read_status_report(sms)
            del sms
            return ret

        if 'ref' in sms:
            ref = sms['ref']
            if ref in self.concat_message:
                self.concat_message[ref].append(sms)
                if len(self.concat_message[ref]) == sms['cnt']:
                    body = ''
                    for m in sorted(self.concat_message[ref], key=itemgetter('seq')):
                        body += m['text']
                    self.concat_message.pop(ref)
                    self.messagemutex.acquire()
                    self.messages.append({
                        'body': body,
                        'date': sms['date'],
                        'address': sms['number'],
                        'status': None
                    })
                    self.messagemutex.release()

                    del sms
                    return True
            else:
                self.concat_message.update({ref: [sms]})
            del sms
            return False
        else:
            self.messagemutex.acquire()
            self.messages.append({
                'body': sms['text'],
                'date': sms['date'],
                'address': sms['number'],
                'status': None
            })
            self.messagemutex.release()
            del sms
            return True

    def event(self):
        """
        Listen on SMS received event

        :returns: True when an SMS is received from device, otherwise False
                  or raise an exception when an error occur
        """
        try:
            line = self.serial.readline()
        except SerialException, msg:
            raise ModemError(msg)

        if line == '':
            return False

        line1 = line
        if isSMSUnsolicited(line1):
            try:
                line2 = self.serial.readline()
            except SerialException, msg:
                raise ModemError(msg)

            atcommand, result = line1.split(' ')
            if line2 == '':
                return False
            return self.read_sms(line2)
        else:
            try:
                self.serial.processline(line)
            except SerialException, msg:
                raise ModemError(msg)

        return False

    def process(self):
        """
        Get unread inbox message

        :returns: a list of messages
        """
        self.messagemutex.acquire()
        messages = self.messages
        self.messages = []
        self.messagemutex.release()
        return messages

    def stop(self):
        """
        Stop listening on serial port
        """
        if not hasattr(self, 'serial'):
            raise ModemError('No modem found')
        try:
            self.serial.close()
        except SerialException, err:
            raise ModemError(err)
