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
Ext.define('JanuaWeb.view.admin.AddAdminWindow', {
    extend: 'Ext.window.Window',
    xtype: 'AddAdminWindow',
    
    requires: ['Ext.ux.PasswordGenerator'],

    title: 'Add a new supervisor',
    resizable: false,
    modal: true,
    layout: 'fit',

    autoShow: true,
    autoScroll: true,

    controller: 'admin',

	viewModel : {
		type: 'admin'
	},

	items: [{
		xtype: 'form',
		reference: 'addAdminForm',
		bodyPadding: 10,
		autoScroll: true,
		width: 400,
		fieldDefaults: {
			labelAlign: 'right',
			labelWidth: 160
		},
		
		defaultType: 'textfield',
		
		defaults: {
			anchor: '100%'
		},

		items: [{
			fieldLabel: 'Authentication method',
			xtype: 'combobox',
			bind: '{admin.auth_backend}',
			queryMode: 'local',
			displayField: 'name',
			editable: false,
			forceSelection: true,
			anchor: '80%',
			valueField: 'name',
			emptyText: 'Select method',
			bind: {
				store: 'AuthBackend',
				value: '{admin.auth_backend}'
			}
		},{
			fieldLabel: 'Login',
			bind: '{admin.login}',
			allowBlank: false
		},{
			fieldLabel: 'Name',
			bind: '{admin.name}',
			allowBlank: false
		},{
			fieldLabel: 'Firstname',
			bind: '{admin.firstname}',
			allowBlank: false
		},{
			fieldLabel: 'Phone number',
			bind: '{admin.phone_number}',
			allowBlank: false,
			vtype: 'phone'
		},{
			fieldLabel: 'Password',
			bind: '{admin.password}',
			hidden: true,
			id: 'p1'
		},{
			fieldLabel: 'Password confirmation',
			id: 'p2',
			vtype: 'password',
			initialPassField: 'p1',
			hidden: true
		},{
			fieldLabel: 'Email',
			bind: '{admin.email}',
			vtype: 'email',
			allowBlank: false
		},{
			fieldLabel: 'SMS/MAIL recipient filter',
			bind: '{admin.recipient_filter}',
			xtype: 'checkbox',
			checked: true,
			inputValue: true,
			uncheckedValue: false
		}],

		buttons: [{
			xtype: 'passgen',
			text: 'Generate password',
			reference: 'generatePassword',
			hidden: true,
			listeners: {
				click: 'onGeneratePasswordCreate'
			}
		},'->',{
			text: 'Create',
			disabled: false,
			formBind: true,
			listeners: {
				click: 'onCreateAdminWindow'
			}
		}]
	}]
});