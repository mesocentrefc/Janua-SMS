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
Ext.define('JanuaWeb.view.group.EditContactWindow', {
	extend: 'Ext.window.Window',
	xtype: 'EditContactWindow',
	
	requires: [
		'JanuaWeb.view.group.ContactViewModel',
		'Ext.view.MultiSelector'
	],
	
	controller: 'contactgroup',
	
	viewModel : {
		type: 'contact'
	},
	
	listeners: {
		close: 'onCloseContactWindow',
		scope: 'controller'
	},
	
	width: 300,
	minHeight: 250,
	height: 450,
	bodyPadding: 10,
	
	autoShow: true,
	autoScroll: true,

	layout: {
		type: 'vbox',
		align: 'stretch'
	},

	bind: 'Edit contact: {contact.name}',

	modal: true,
	
	items: [{
		xtype: 'textfield',
		fieldLabel: 'Firstname',
		reference: 'editContactFirstname',
		labelWidth: 70,
		allowBlank: false,

		bind: '{contact.firstname}'
	},{
		xtype: 'textfield',
		fieldLabel: 'Name',
		reference: 'editContactName',
		labelWidth: 70,
		allowBlank: false,
		
		bind: '{contact.name}'
	},{
		xtype: 'textfield',
		fieldLabel: 'Phone',
		reference: 'editContactPhone',
		labelWidth: 70,
		vtype: 'phone',
		allowBlank: false,

		bind: '{contact.phone_number}'
	},{
		xtype: 'textfield',
		vtype: 'email',
		fieldLabel: 'Email',
		labelWidth: 70,
		allowBlank: true,
		reference: 'editContactMail',

		bind: '{contact.email}'
	},{
		xtype: 'textfield',
		fieldLabel: 'Description',
		labelWidth: 70,
		allowBlank: true,

		bind: '{contact.description}'
	},{
		xtype: 'multiselector',
		bind: '{contact.groups}',

		viewConfig: {
			deferEmptyText: false,
			emptyText: 'No group selected'
		},

		removeRowTip: 'Remove this group',
		addToolText: 'Search for groups to add',
		
		title: 'Groups',
		flex: 1,
		margin: '10 0',
		search: {
			closeAction: 'hide',
			closable: true,
			title: 'Group selection',
			height: 300,
			store: {
				model: 'Group',
				pageSize: 0
			}
		}
	}],

	buttons: [{
		text: 'Save',
		formBind: true,
		listeners: {
			click: 'onSaveContactWindow'
		}
	}]
});
