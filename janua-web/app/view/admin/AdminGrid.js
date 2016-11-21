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
Ext.define('JanuaWeb.view.admin.AdminGrid', {
	extend: 'Ext.grid.Panel',
	alias: 'widget.AdminGrid',
	
	controller: 'admin',
	
	stateful: true,
	layout: 'fit',
	flex: 1,
	
	store: 'Admin',

	tools:[{
		type: 'plus',
		tooltip: 'Add supervisor',
		handler: 'onAddAdminClick'
	}],

	dockedItems: [{
		xtype: 'pagingtoolbar',
		store: 'Admin',
		dock: 'top',
		displayInfo: true
	}],

	columns: [{
		dataIndex: 'name',
		text: 'Name'
	},{
		dataIndex: 'firstname',
		text: 'Firstname'
	},{
		dataIndex: 'phone_number',
		text: 'Phone number',
		flex: 0.5
	},{
		xtype: 'booleancolumn',
		dataIndex: 'has_client',
		text: 'Has client ?',
		falseText: 'No',
		trueText: 'Yes'
	},{
		dataIndex: 'level',
		text: 'Access level',
		renderer: 'onRenderAdminLevel'
	},{
		dataIndex: 'sms_quota',
		text: 'SMS quota',
		flex: 0.5,
		renderer: 'onRenderAdminQuota'
	},{
		dataIndex: 'email',
		flex: 1,
		text: 'Email'
	},{
		dataIndex: 'auth_backend',
		text: 'Authentication'
	},{
		xtype: 'booleancolumn',
		dataIndex: 'recipient_filter',
		text: 'SMS/MAIL recipient filter ?',
		falseText: 'No',
		trueText: 'Yes',
		flex: 1
	},{
		xtype: 'widgetcolumn',
		text: 'Edit',
		width: 90,
		widget: {
			xtype: 'button',
			text: 'Edit',
			handler: 'onEditAdminClick'
		}
	},{
		xtype: 'widgetcolumn',
		text: 'Delete',
		width: 90,
		widget: {
			xtype: 'button',
			text: 'Delete',
			handler: 'onDeleteAdminClick'
		}
	}]
})