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
Ext.define('JanuaWeb.view.group.ContactGrid', {
	extend: 'Ext.grid.Panel',
	xtype: 'ContactGrid',
	
	controller: 'contactgroup',
	
	stateful: true,
	store: 'Contact',
	layout: 'fit',

	reference: 'contactGrid',

	tools:[{
		type: 'plus',
		tooltip: 'Add contact',
		handler: 'onAddContactClick'
	}],

	dockedItems: [{
		xtype: 'pagingtoolbar',
		store: 'Contact',
		dock: 'top',
		displayInfo: true
	},{
		xtype: 'textfield',
		dock: 'top',
		emptyText: 'Search a contact name ...',
		listeners: {
			change: 'onSearchContact',
			buffer: 300
		}
	}],
	columns: [{
		dataIndex: 'name',
		flex: 0.7,
		text: 'Name'
	},{
		dataIndex: 'firstname',
		flex: 0.7,
		text: 'Firstname'
	},{
		dataIndex: 'phone_number',
		flex: 0.5,
		text: 'Phone number'
	},{
		dataIndex: 'email',
		flex: 1,
		text: 'Email'
	},{
		dataIndex: 'description',
		flex: 1,
		text: 'Description'
	},{
		xtype: 'widgetcolumn',
		width: 90,
		text: 'Edit',
		widget: {
			xtype: 'button',
			text: 'Edit',
			handler: 'onEditContactClick'
		}
	},{
		xtype: 'widgetcolumn',
		width: 90,
		text: 'Delete',
		widget: {
			xtype: 'button',
			text: 'Delete',
			handler: 'onDeleteContactClick'
		}
	}]
})