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
Ext.define('JanuaWeb.view.group.EditGroupWindow', {
    extend: 'Ext.window.Window',
    xtype: 'EditGroupWindow',
    
    requires: [
		'JanuaWeb.view.group.GroupViewModel',
		'Ext.view.MultiSelector'
	],
	
    controller: 'contactgroup',
	
	viewModel : {
		type: 'group'
	},
	
	listeners: {
		close: 'onCloseGroupWindow',
		scope: 'controller'
	},

    resizable: false,
    modal: true,
    layout: 'fit',

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

	bind: 'Edit group: {group.name}',

	items: [{
		xtype: 'textfield',
		fieldLabel: 'Name',
		reference: 'editGroupName',
		labelWidth: 70,
		allowBlank: false,
		vtype: 'group',

		bind: '{group.name}'
	},{
		xtype: 'textfield',
		fieldLabel: 'Description',
		labelWidth: 70,
		allowBlank: true,

		bind: '{group.description}'
	},{
		xtype: 'multiselector',
		bind: '{group.contacts}',

		fieldName: 'fullname',
		
		viewConfig: {
			deferEmptyText: false,
			emptyText: 'No contact selected'
		},

		removeRowTip: 'Remove this contact',
		addToolText: 'Search for contacts to add',

		title: 'Contacts',
		flex: 1,
		margin: '10 0',
		search: {
			closeAction: 'hide',
			closable: true,
			height: 300,
			title: 'Contact selection',
			store: {
				model: 'Contact',
				pageSize: 0
			}
		}
	}],

	buttons: [{
		text: 'Save',
		formBind: true,
		listeners: {
			click: 'onSaveGroupWindow'
		}
	}]
});
