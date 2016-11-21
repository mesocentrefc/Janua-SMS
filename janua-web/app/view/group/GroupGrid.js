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
Ext.define('JanuaWeb.view.group.GroupGrid', {
	extend: 'Ext.grid.Panel',
	xtype: 'GroupGrid',
	
	controller: 'contactgroup',

	reference: 'groupGrid',

	stateful: true,
	store: 'Group',
	layout: 'fit',

	tools:[{
		type: 'plus',
		tooltip: 'Add group',
		handler: 'onAddGroupClick'
	}],
	
	dockedItems: [{
		xtype: 'pagingtoolbar',
		store: 'Group',
		dock: 'top',
		displayInfo: true
	},{
		xtype: 'textfield',
		dock: 'top',
		emptyText: 'Search a group name ...',
		listeners: {
			change: 'onSearchGroup',
			buffer: 300
		}
	}],

	columns: [{
		dataIndex: 'name',
		flex: 0.7,
		text: 'Name'
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
			handler: 'onEditGroupClick'
		}
	},{
		xtype: 'widgetcolumn',
		width: 90,
		text: 'Delete',
		widget: {
			xtype: 'button',
			text: 'Delete',
			handler: 'onDeleteGroupClick'
		}
	}]
})