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
Ext.define('JanuaWeb.view.admin.LogGrid', {
	extend: 'Ext.grid.Panel',
	alias: 'widget.LogGrid',
	
	controller: 'admin',
	
	stateful: true,
	store: 'Sms',
	layout: 'fit',
	flex: 1,
	
	dockedItems: [{
		xtype: 'pagingtoolbar',
		store: 'Sms',
		dock: 'top',
		displayInfo: true
	}],

	columns: [{
		xtype: 'datecolumn',
		dataIndex: 'date_time',
		flex: 1,
		text: 'Date',
		format: 'Y-m-d H:i:s'
	},{
		xtype: 'booleancolumn',
		dataIndex: 'authorized',
		text: 'Authorized ?',
		falseText: 'No',
		trueText: 'Yes'
	},{
		dataIndex: 'sender',
		flex: 1,
		text: 'Sender'
	},{
		dataIndex: 'recipient',
		flex: 1,
		text: 'Recipient'
	},{
		dataIndex: 'raw_message',
		flex: 1,
		text: 'Message'
	},{
		dataIndex: 'status',
		flex: 1,
		text: 'Status',
		renderer: function(rec) {
			if (rec == 4) {
				return "Received";
			} else if (rec == 3) {
				return "Not supported";
			} else if (rec == 2) {
				return "Sent/Unknown";
			} else if (rec == 1) {
				return "Sent/Delivered";
			} else if (rec == 0) {
				return "Sent";
			}
		}
	}]
})