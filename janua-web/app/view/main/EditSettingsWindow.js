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
Ext.define('JanuaWeb.view.admin.EditSettingsWindow', {
    extend: 'Ext.window.Window',

    xtype: 'EditSettingsWindow',

    requires: ['JanuaWeb.view.admin.AdminViewModel'],
    
    controller: 'main',
    
    viewModel : {
        type: 'admin'
    },

    listeners: {
        close: 'onCloseSettingsWindow',
        scope: 'controller'
    },

    bind: 'Account information',

    resizable: false,
    modal: true,
    layout: 'fit',
    autoShow: true,
    autoScroll: true,

    items: [{
        xtype: 'form',
        reference: 'editSettingsForm',
        bodyPadding: 10,
        autoScroll: true,
        width: 400,
        fieldDefaults: {
            labelAlign: 'right',
            labelWidth: 140
        },
        
        defaultType: 'textfield',
        
        defaults: {
            anchor: '100%'
        },

        items: [
            { fieldLabel: 'Login', bind: '{admin.login}', allowBlank: false, disabled: true },
            { fieldLabel: 'Authentication method', bind: '{admin.auth_backend}', allowBlank: false, disabled: true },
            { fieldLabel: 'Name', bind: '{admin.name}', allowBlank: false },
            { fieldLabel: 'Firstname', bind: '{admin.firstname}', allowBlank: false},
            { fieldLabel: 'Phone number', bind: '{admin.phone_number}', vtype: 'phone', allowBlank: false, disabled: true},
            { fieldLabel: 'Email', bind: '{admin.email}', vtype: 'email', allowBlank: false},
            {
                fieldLabel: 'Change password',
                reference: 'changePassword',
                xtype: 'checkbox',
                listeners: {
                    change: 'onChangePassword'
                }
            },
            {
                fieldLabel: 'Password',
                id: 'myp1',
                allowBlank: true,
                inputType: 'password',
                bind: {
                    disabled: '{!changePassword.checked}'
                }
            },
            {
                fieldLabel: 'Password confirmation',
                id: 'myp2',
                allowBlank: true,
                vtype: 'password',
                inputType: 'password',
                initialPassField: 'myp1',
                bind: {
                    disabled: '{!changePassword.checked}'
                }
            }
        ],

        buttons: [{
            text: 'Save',
            formBind: true,
            listeners: {
                click: 'onSaveSettingsWindow'
            }
        }]
    }]
});
