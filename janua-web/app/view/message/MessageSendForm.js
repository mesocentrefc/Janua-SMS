/**
 * Copyright (c) 2016 Cédric Clerget - HPC Center of Franche-Comté University
 *
 * This file is part of Janua-SMS
 *
 * http://github.com/mesocentrefc/Janua-SMS
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation v2.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
Ext.define('JanuaWeb.view.message.MessageSendForm', {
    extend: 'Ext.form.Panel',
    xtype: 'sendform',
    alias: 'widget.MessageSendForm',
    
    buttonAlign: 'left',

    fieldDefaults: {
        labelAlign: 'top',
        labelWidth: 120,
        anchor: '100%'
    },

    bodyPadding: 5,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    autoScroll: true,

    items: [{
        labelAlign: 'left',
        fieldLabel: 'Send to all contacts',
        reference: 'sendAll',
        xtype: 'checkbox',
        name: 'sendall'
    },{
        xtype: 'fieldset',
        title: 'RECIPIENT',
        items: [{
            xtype: 'combobox',
            fieldLabel: 'To group',
            reference: 'smsGroup',
            name: 'groups',
            multiSelect: true,
            queryMode: 'remote',
            displayField: 'name',
            autoLoadOnValue: true,
            editable: false,
            valueField: 'name',
            store: new JanuaWeb.store.Group({pageSize: 0}),
            listConfig: {maxHeight: 200},
            listeners: {
                expand: 'onComboExpand',
                destroy: 'onComboDestroy',
                single: true
            },
            bind: {
                disabled: '{sendAll.checked}'
            }
        },{
            xtype: 'combobox',
            fieldLabel: 'To contact',
            reference: 'smsContact',
            name: 'contacts',
            queryMode: 'remote',
            multiSelect: true,
            editable: false,
            displayField: 'display',
            valueField: 'phone_number',
            store: new JanuaWeb.store.Contact({pageSize: 0}),
            listConfig: {maxHeight: 200},
            listeners: {
                expand: 'onComboExpand',
                destroy: 'onComboDestroy',
                single: true
            },
            bind: {
                disabled: '{sendAll.checked}'
            }
        }]
    },{
        xtype: 'fieldset',
        title: 'SMS',
        items: [{
            fieldLabel: 'Your message (characters remaining: 480)',
            reference: 'smsMessage',
            xtype: 'textarea',
            emptyText: 'Message goes here',
            name: 'message',
            maxLength : 480,
            enableKeyEvents: true,
            listeners: {
                keydown: 'onUpdateCounter',
                keyup: 'onUpdateCounter'
            },
            allowBlank: false
        }]
    },{
        labelAlign: 'left',
        fieldLabel: 'Send email',
        reference: 'sendMail',
        xtype: 'checkbox',
        name: 'sendmail'
    },{
        xtype: 'fieldset',
        title: 'EMAIL',
        items: [{
            xtype: 'textfield',
            fieldLabel: 'Mail subject',
            reference: 'mailSubject',
            emptyText: 'Mail subject goes here',
            name: 'mail_subject',
            allowBlank: true,
            bind: {
                disabled: '{!sendMail.checked}'
            }
        },{
            height: 200,
            fieldLabel: 'Mail body',
            reference: 'mailBody',
            xtype: 'textarea',
            emptyText: 'Mail body goes here',
            name: 'mail_message',
            allowBlank: true,
            bind: {
                disabled: '{!sendMail.checked}'
            }
        }]
    }],
    buttons: [{
        text: 'Send',
        formBind: true,
        handler: 'onSendMessage'
    }]
})
