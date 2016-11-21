Persistent queue
----------------

Persistent queue are used to store mail and SMS message for further sending

.. autoclass:: janua.utils.sqlite_queue.PersistentSqliteQueue
   :members:
   :special-members: __init__

.. _mail_queue:

Mail queue
~~~~~~~~~~

Mail queue accept mail object only (:class:`janua.utils.mail.MailObj`):

  .. code-block:: python
 
     from janua import mail_queue

     mail_queue.put(mailobj)

Sms queue
~~~~~~~~~

Sms queue take a tuple containing:

  * message to send
  * recipient phone number
  * admin database object id which send the message

  .. code-block:: python

     from janua import sms_queue
     
     sms_queue.put((message, phone_number, admin_id))