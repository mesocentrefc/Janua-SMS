.. figure:: http://janua-sms.readthedocs.io/en/latest/_static/logo_janua.svg

An active SMS gateway
=====================

**Janua-SMS** is a SMS gateway written in `python <http://www.python.org>`_, like others
traditional SMS gateways, you can send and receive SMS with focus on high flexibility and
customization to ease integration in IT infrastructure.

For hurry people, here the `documentation <http://janua-sms.readthedocs.io/>`_

Features
--------

* **Multi-user support**
* **Web administration interface**
* **Groups and contacts management**
* **Multipart SMS**
* **Send alerts** to contact or groups via SMS/MAIL
* **Custom defined actions** triggered on received SMS with ACLs and authentication control (home automation, surveys, services ...)
* **Authentication plugins**
* **Mail templates**
* **SMS quota management**
* **Restful API** for integration with third-party applications (Nagios, Zabbix ...)
* **Support serial modems** and turn **Android phones** as modem (if you have old android phone to recycle)

Requirements
------------

* Python 2.6 minimum (python 3 is not supported at this time)
* Linux 32/64 bits, tested on Raspberry PI too but require ADB arm binary to be installed since it's not included in package
* A serial/USB modem supporting AT commands or an Android phone (only 4.3 SDK versions and below have been tested)

Hardware overview
-----------------

.. figure:: http://janua-sms.readthedocs.io/en/latest/_static/schema_env_janua.jpg
   :align: center