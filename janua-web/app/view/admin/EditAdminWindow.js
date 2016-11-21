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
Ext.define('JanuaWeb.view.admin.EditAdminWindow', {
    extend: 'Ext.window.Window',

    xtype: 'EditAdminWindow',

    requires: ['JanuaWeb.view.admin.AdminViewModel'],

	controller: 'admin',
	
	viewModel : {
		type: 'admin'
	},
	
	listeners: {
		close: 'onCloseAdminWindow',
		scope: 'controller'
	},

	bind: 'Edit admin entry {admin.name}',

    resizable: false,
    modal: true,
    layout: 'fit',
    autoShow: true,
    autoScroll: true,
	
    items: [{
    	xtype: 'form',
    	reference: 'editAdminForm',
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
			fieldLabel: 'Auth backend',
			xtype: 'combobox',
			bind: '{admin.auth_backend}',
			queryMode: 'local',
			displayField: 'name',
			editable: false,
			valueField: 'name',
			forceSelection: true,
			bind: {
				store: 'AuthBackend',
				value: '{admin.auth_backend}'
			},
			allowBlank: false
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
			vtype: 'phone',
			allowBlank: false
		},{
			fieldLabel: 'Email',
			bind: '{admin.email}',
			vtype: 'email',
			allowBlank: false
		},{
			xtype: 'fieldcontainer',
			fieldLabel: 'SMS quota',
			defaultType: 'textfield',
			layout: 'hbox',
			items: [{
				xtype: 'numberfield',
				name: 'quota_limit',
				bind: '{admin.quota_limit}',
				id: 'quota_limit',
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
				id: 'quota_unit',
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
			fieldLabel: 'SMS/MAIL recipient filter',
			bind: '{admin.recipient_filter}',
			xtype: 'checkbox',
			checked: true,
			inputValue: true,
			uncheckedValue: false
		},{
			fieldLabel: 'Change password',
			reference: 'changePassword',
			xtype: 'checkbox',
			listeners: {
				change: 'onChangePassword'
			}
		},{
			fieldLabel: 'Password',
			id: 'adp1',
			allowBlank: true,
			bind: {
				disabled: '{!changePassword.checked}'
			}
		},{
			fieldLabel: 'Password confirmation',
			id: 'adp2',
			allowBlank: true,
			vtype: 'password',
			initialPassField: 'adp1',
			bind: {
				disabled: '{!changePassword.checked}'
			}
		}],

    	buttons: [{
			xtype: 'passgen',
			text: 'Generate password',
			reference: 'generatePasswordButton',
			disabled: true,
			listeners: {
				click: 'onGeneratePasswordEdit'
			}
		},'->',{
    		text: 'Save',
    		disabled: true,
    		formBind: true,
			listeners: {
				click: 'onSaveAdminWindow'
			}
    	}]
    }]
});