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
Ext.define('JanuaWeb.view.login.Login', {
    extend: 'Ext.form.Panel',
    
    requires: [
        'JanuaWeb.view.login.LoginController',
        'JanuaWeb.view.login.LoginModel',
        'Ext.form.Panel',
        'Ext.button.Button',
        'Ext.form.field.Text',
        'Ext.form.field.ComboBox'
    ],
    
    viewModel: 'login',
    id: 'login-form',
    controller: 'login',
    bodyPadding: 10,
    title: 'Login - JanuaWeb',

    frame: true,

    width: 305,

    autoEl: {
        tag: 'form',
        method: 'post',
        action: 'login'
    },
    
    items: [{
        xtype: 'textfield',
        name: 'username',
        bind: '{username}',
        fieldLabel: 'Username',
        allowBlank: false,
        listeners: {
            afterrender: function() {
                this.inputEl.set({
                    'autocomplete': 'on'
                });
            }
        }
    }, {
        xtype: 'textfield',
        name: 'password',
        inputType: 'password',
        fieldLabel: 'Password',
        allowBlank: false,
        listeners: {
            afterrender: function() {
                this.inputEl.set({
                    'autocomplete': 'on'
                });
            }
        }
    }, {
        xtype: 'combobox',
        name: 'language',
        fieldLabel: 'Language',
        queryMode: 'local',
        editable: false,
        forceSelection: true,
        displayField: 'name',
        valueField: 'id',
        bind: {
            store: 'Languages',
            value: {
                twoWay: false,
                bindTo: '{defaultLanguage}'
            }
        }
    }],

    buttons: [{
        text: 'Login',
        width: 75,
        height: 25,
        listeners: {
            click: 'onLoginClick',
            afterrender: function() {
                this.el.createChild({
                    tag: 'input',
                    type: 'submit',
                    style: 'width: 100px; height: 35px; position: relative; top: -31px; left: -4px; opacity: 0;'
                });
            }
        }
    }]
});
