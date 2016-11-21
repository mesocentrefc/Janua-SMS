.. _quickstart:

Quickstart
==========

Install Janua-SMS
------------------------

You can download it from github at url https://www.github.com/mesocentrefc/Janua-SMS.

Before setup installation, you must install these packages:

* **Debian/Ubuntu**: ``apt-get install python-pip python-setuptools python-dev libsqlite3-dev libldap2-dev libsasl2-dev``
* **Redhat/Centos/Fedora**: ``yum install python-pip python-setuptools python-dev``

Recommended way to install (as root user):

* **With pip**: ``pip install janua-sms``
* **From source**: ``python setup.py install``

By default, the installation directory is **/opt/janua** (this directory will be taken in documentation)

Configure Janua-SMS
-------------------

**1.** After installation, it's recommended to create a specific user and group for Janua-SMS (**don't run it as root**)::

   # adduser --system --group --no-create-home janua

**2.** Edit server configuration in **/opt/janua/conf/server.cfg**

**3.** Configure the modem

   * **General**

   **sms** section to configure the type of modem and some parameters related to SMS configuration:

      * **type:** choose between serial and android
      * **phone_number:** indicate sim card phone number
      * **pin_code:** SIM pin code (serial mode only)
      * **send_interval:** time in seconds between every SMS sending
      * **prefix_filter:** authorized prefixes number separated by commas

   * **Serial/USB modem**

   Check your modem manual to install and configure it, after successful installation modify the **serial**
   section in the server configuration:

      * **port:** you can specify multiple serial ports separated by commas
      * **baud:** baud rate setting, depend of your modem speed line
      * **bytesize:** bytesize setting
      * **parity:** parity setting
      * **stopbits:** stop bits setting
      * **xonxoff:** XON/XOFF setting
      * **rtscts:** RTS/CTS flow control setting
      * **dsrdtr:** DSR/DTR flow control setting
      * **timeout:** timeout setting in second between each sent SMS (modem often freeze if this timeout is too low)
      * **status_report:** enable or disable SMS status report

   * **Android phone**

   Android is the easiest setup, only two steps on android phone:

      * enable USB debug mode (`How to enable USB debug mode <https://www.recovery-android.com/enable-usb-debugging-on-android.html>`_)
      * disable PIN code confirmation (not required but in case phone reboot/crash for some reasons)

**4.** Configure the web interface

   **web** section server configuration:

   * **bind_address:** address to bind web interface (default **0.0.0.0** for any interfaces)
   * **hostname:** web server hostname (default **localhost**)
   * **port:** web server port (default **5000**)
   * **url:** public root url (eg: **http://janua.mydomain.com/**)
   * **secure_connection:** enable HTTPS (highly recommended)
   * **session_lifetime:** web session lifetime in hour (default **12**)
   * **ssl_certificate:** SSL certificate (if **secure_connection=True**)
   * **ssl_private_key:** SSL private key certificate (if **secure_connection=True**)

**5.** Configure mailer

   If mail is disable, features like critical error report, accounts creation/update/deletion notifications won't work

   * **enable:** enable or disable mail sending
   * **smtp_host:** SMTP server
   * **smtp_port:** SMTP port
   * **smtp_username:** SMTP username account **(optional if behind SMTP relay server)**
   * **smtp_password:** SMTP password account **(optional if behind SMTP relay server)**
   * **smtp_tls:** use TLS
   * **smtp_ssl:** use SSL
   * **mail_from:** mail address which mail come from
   * **mail_language:** Mail templates languages to use

Start Janua-SMS
---------------

Before starting Janua-SMS, you must create an administrator account otherwise Janua-SMS will not start.

To create it, type the following command and follow the instructions::

# /etc/init.d/janua action admin --operation add

Before starting Janua-SMS as a daemon, it could be fine to test your modem configuration, you can start it with dev option::

# /etc/init.d/janua dev

All debug/information/errors messages will be displayed on output to check your configuration if some errors appears.

To start Janua-SMS::

# /etc/inid.d/janua start

See :ref:`commands <cli>` available.

Now you can connect to :ref:`web interface <web_interface>` at url set in **web** section of your configuration file.