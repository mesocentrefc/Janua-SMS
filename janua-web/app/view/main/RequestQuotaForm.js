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
Ext.define('JanuaWeb.view.main.RequestQuotaForm', {
    extend: 'Ext.form.Panel',

    xtype: 'RequestQuotaForm',

    controller: 'main',

    viewModel : {
        type: 'admin'
    },

    resizable: false,
    modal: true,
    floating: true,
    closable: true,
    frame: true,
    
    layout: 'anchor',

    autoShow: true,
    autoScroll: false,

    listeners: {
        close: 'onCloseSettingsWindow',
        scope: 'controller'
    },

    title: 'Request SMS quota',
    width: 400,
    bodyPadding: 10,

    items: [{
        xtype: 'fieldcontainer',
        fieldLabel: 'SMS quota',
        defaultType: 'textfield',
        layout: 'hbox',
        items: [{
            xtype: 'numberfield',
            name: 'quota_limit',
            bind: '{admin.quota_limit}',
            reference: 'quotaLimit',
            step: 10,
            flex: 0.5
        },{
            xtype: 'splitter'
        },{
            xtype: 'displayfield',
            value: 'per'
        },{
            xtype: 'splitter'
        },{
            xtype: 'combobox',
            name: 'quota_unit',
            bind: '{admin.quota_unit}',
            reference: 'quotaUnit',
            queryMode: 'local',
            displayField: 'name',
            editable: false,
            valueField: 'id',
            flex: 0.5,
            bind: {
                store: 'QuotaUnit',
                value: '{admin.quota_unit}'
            }
        }]
    },{
        xtype: 'component',
        html: '<br/><b>Your request will be sent to Janua-SMS administrator which ' +
              'will accept it or not.<br/>If your request is accepted, you will ' +
              'receive an email with your new quota.</b>',
        margin: 0
    }],

    buttons: [{
        text: 'Send',
        formBind: true,
        handler: 'onSendRequestQuota'
    }]
});
