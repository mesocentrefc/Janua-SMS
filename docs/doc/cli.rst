.. _cli:

Command line interface
======================

General
-------
Janua wrapper::

    /etc/init.d/janua

Switch options:

+--------------+----------------------------------------------------------+
| **start**    | Start Janua-SMS daemon                                   |
+--------------+----------------------------------------------------------+
| **stop**     | Stop Janua-SMS daemon                                    |
+--------------+----------------------------------------------------------+
| **restart**  | Restart Janua-SMS daemon                                 |
+--------------+----------------------------------------------------------+
| **status**   | Return Janua-SMS status                                  |
+--------------+----------------------------------------------------------+
| **version**  | Return Janua-SMS version                                 |
+--------------+----------------------------------------------------------+
| **debug**    | Start Janua-SMS daemon with debug log level enabled      |
+--------------+----------------------------------------------------------+
| **dev**      | Start Janua-SMS with debug log level enabled (no daemon) |
+--------------+----------------------------------------------------------+
| **reload**   | Reload actions and authentication plugins wihtout restart|
+--------------+----------------------------------------------------------+
| **action**   | action switch                                            |
+--------------+----------------------------------------------------------+
| **test**     | unit test switch (same as action)                        |
+--------------+----------------------------------------------------------+

Supervisor management
---------------------

To manage supervisor, use **admin** action switch::

    /etc/init.d/janua action admin

Available options for **admin**:

  * ``--operation``: Take **add** or **delete** as value

* To add a supervisor::

    /etc/init.d/janua action admin --operation add

* To delete a supervisor::

    /etc/init.d/janua action admin --operation delete

SMS
---

To send SMS from console, use **sendsms** action switch::

    /etc/init.d/janua action sendsms

Available options for **sendsms**:
  * ``--message``: Message to send
  * ``--to``: Recipients (phone numbers, groups name)

* To send a SMS to +33123456789::

    /etc/init.d/janua action sendsms --message="Test" --to="+33123456789"

SMS log
-------

To view, export SMS log, use **log** action switch::

    /etc/init.d/janua action log

Available options for **log**:
  * ``--operation``: take **view, delete or view_admin** as value
  * ``--output``: write log in CSV format into file
  * ``--startdate``: take log from start date (date format: **YYYY/MM/DD**)
  * ``--enddate``: take log until end date (date format: **YYYY/MM/DD**)

* To extract all SMS log and store into /tmp/sms.log::

    /etc/init.d/janua action log --operation view --output=/tmp/sms.log

* To view SMS log specific to a supervisor::

    /etc/init.d/janua action log --operation view_admin
    Select an admin number to display only these logs :
    0. Admin Test
    Enter a number (or ENTER to quit): 0

Maintenance
-----------

To announce a maintenance operation to supervisor::

    /etc/init.d/janua action maintenance

Available options for **maintenance**:
  * ``--duration``: Maintenance duraction in hour
  * ``--start_date``: Maintenance start at date (date format: **YYYY/MM/DD**)
  * ``--start_time``: Maintenance start at time

* To send a mail to all supervisor to announce a maintenance operation::

    /etc/init.d/janua action maintenance --duration 1 --start_date 2016/10/19 --start_time="12:00 pm"