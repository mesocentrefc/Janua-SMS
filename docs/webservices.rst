Web services
============

All web services require authentication, you can use Auth Basic
authentication by using your credentials:

http://login:password@janua.mydomain.com/get_sms_config

Or by requesting a authentication token **JanuaAuthToken** and put it as HTTP
header in all your requests

**Authentication**
------------------

login
~~~~~

**URL: http://janua.mydomain.com/login**

.. autofunction:: janua.ws.services.login

logout
~~~~~~

**URL: http://janua.mydomain.com/logout**

.. autofunction:: janua.ws.services.logout

**Authentication backends**
---------------------------

list_auth_backend
~~~~~~~~~~~~~~~~~

**URL: http://janua.mydomain.com/list_auth_backend (GET method)**

.. autoclass:: janua.actions.list_auth_backend.ListAuthBackend

get_auth_backend
~~~~~~~~~~~~~~~~

**URL: http://janua.mydomain.com/get_auth_backend/<backend> (GET method)**

.. autoclass:: janua.actions.get_auth_backend.GetAuthBackend

set_auth_backend
~~~~~~~~~~~~~~~~

**URL: http://janua.mydomain.com/set_auth_backend/<backend> (POST method)**

.. autoclass:: janua.actions.set_auth_backend.SetAuthBackend

**SMS / Mail**
--------------

sendsms
~~~~~~~

**URL: http://janua.mydomain.com/sendsms**

.. autoclass:: janua.actions.sendsms.SendSms

sendmail
~~~~~~~~

**URL: http://janua.mydomain.com/sendmail**

.. autoclass:: janua.actions.sendmail.SendMail

sms-usage
~~~~~~~~~

**URL: http://janua.mydomain.com/sms-usage**

.. autoclass:: janua.actions.sms_usage.SmsUsage

sms-stats
~~~~~~~~~

**URL: http://janua.mydomain.com/sms-stats**

.. autoclass:: janua.actions.sms_stats.SmsStats

**Action configuration**
------------------------

get_sms_config
~~~~~~~~~~~~~~

**URL: http://janua.mydomain.com/get_sms_config**

.. autoclass:: janua.actions.get_sms_config.GetSmsConfig

!! TODO !!

get_web_config
~~~~~~~~~~~~~~

**URL: http://janua.mydomain.com/get_web_config**

.. autoclass:: janua.actions.get_web_config.GetWebConfig

!! TODO !!

**Restful API**
---------------

Restful API is based on `Flask-Restless <https://flask-restless.readthedocs.io/en/0.17.0/>`_.

To use the followings API, please refer to Flask-Restless
`format of requests and response <https://flask-restless.readthedocs.io/en/0.17.0/requestformat.html>`_ documentation

.. _contact_rest_api:

CONTACT
~~~~~~~

.. automodule:: janua.ws.api.contact

.. _group_rest_api:

GROUP
~~~~~

.. automodule:: janua.ws.api.group

CONTACT_GROUP
~~~~~~~~~~~~~

.. automodule:: janua.ws.api.contact_group

SMS
~~~

.. automodule:: janua.ws.api.sms

ADMIN
~~~~~

.. automodule:: janua.ws.api.admin

ACTION
~~~~~~

.. automodule:: janua.ws.api.action

AUTHORIZED_GROUP_ACTION
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: janua.ws.api.authorized_group_action

AUTHORIZED_SUPERVISOR_ACTION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: janua.ws.api.authorized_supervisor_action

CONTACT_NOTIFY_ACTION
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: janua.ws.api.contact_notify_action
