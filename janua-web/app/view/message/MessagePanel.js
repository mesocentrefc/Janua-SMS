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
Ext.define('JanuaWeb.view.message.MessagePanel', {
	extend: 'Ext.panel.Panel',
	xtype: 'compose-panel',
	alias: 'widget.MessagePanel',
	
	requires: [
		'JanuaWeb.view.message.MessageController',
		'JanuaWeb.view.message.MessageLogGrid',
		'JanuaWeb.view.message.MessageStatsGraph',
		'JanuaWeb.view.message.MessageSendForm'
	],
    
    controller: 'message',

    bodyPadding: 5,
    layout: {
        type: 'hbox',
		align: 'stretch'
    },
	
    items: [{
		title: 'Send message',
		xtype: 'MessageSendForm',
		frame: true,
		flex: 1,
		reference: 'smsForm'
    },{
		xtype: 'container',
		layout: {
			type: 'vbox',
			align: 'stretch'
		},
		flex: 1,
		margin: '0 0 0 5',
		items: [{
			title: 'Message statistics for current year',
			xtype: 'MessageStatsGraph',
			frame: true,
			flex: 1,
			margin: '0 0 5 0'
		},{
			title: 'SMS log message',
			xtype: 'MessageLogGrid',
			frame: true,
			flex: 1
		}]
		
	}]
});
