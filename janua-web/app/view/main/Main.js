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
Ext.define('JanuaWeb.view.main.Main', {
    extend: 'Ext.container.Viewport',

    requires: [
        'JanuaWeb.view.main.MainController',
        'JanuaWeb.view.main.MainModel',
        'JanuaWeb.view.message.MessagePanel',
        'JanuaWeb.view.group.ContactGroupPanel',
        'JanuaWeb.view.admin.AdminPanel',
		'JanuaWeb.view.action.ActionPanel',
		'JanuaWeb.view.admin.SupervisorPanel',
		'JanuaWeb.view.main.HomePanel',
		'JanuaWeb.view.main.MyAccountMenu',
		'JanuaWeb.view.main.ContactsGroupsMenu',
		'JanuaWeb.view.main.AuthenticationMenu'
    ],

    xtype: 'app-main',
    controller: 'main',
	
    layout: 'fit',

    viewModel: {
        type: 'main'
    },

	items: [{
		xtype: 'tabpanel',
		reference: 'mainTab',
		header: {
			layout: {
				align: 'stretchmax'
			},
			glyph: 61
		},
		bind: {
			title: '{name}'
		},
		tabPosition: 'left',
		tabRotation: 0,

		tools:[{
			xtype: 'displayfield',
			reference: 'smsUsage',
			cls: 'smsusage'
		},{
			xtype: 'button',
			text: 'Authentication',
			reference: 'authenticationMenu',
			menuAlign: 'tr-br?',
			menu: {
				xtype: 'AuthenticationMenu'
			},
			margin: '0 0 0 8'
		},{
			xtype: 'button',
			text: 'Contacts/Groups',
			menuAlign: 'tr-br?',
			menu: {
				xtype: 'ContactsGroupsMenu'
			},
			margin: '0 0 0 8'
		},{
			xtype: 'button',
			text: 'My account',
			menuAlign: 'tr-br?',
			menu: {
				xtype: 'MyAccountMenu'
			},
			margin: '0 0 0 8'
		}],
		
		items:[{
			title: 'Home',
			xtype: 'HomePanel'
		},{
			title: 'Message',
			xtype: 'MessagePanel',
			bodyCls: 'background'
		},{
			title: 'Groups and Contacts',
			xtype: 'ContactGroupPanel',
			bodyCls: 'background'
		},{
			title: 'Administration',
			xtype: 'AdminPanel',
			reference: 'adminPanel',
			bodyCls: 'background'
		},{
			title: 'Supervision',
			xtype: 'SupervisorPanel',
			reference: 'supervisorPanel',
			bodyCls: 'background'
		},{
			title: 'Action ACLs',
			xtype: 'ActionPanel',
			reference: 'actionPanel',
			bodyCls: 'background'
		}]
	}]

});
