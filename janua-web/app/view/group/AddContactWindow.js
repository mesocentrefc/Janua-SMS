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
Ext.define('JanuaWeb.view.group.AddContactWindow', {
    extend: 'Ext.window.Window',
    xtype: 'AddContactWindow',
	
    title: 'Add a new contact',
    resizable: false,
    modal: true,
    layout: 'fit',

    autoShow: true,
    autoScroll: true,
    
    controller: 'contactgroup',

	viewModel : {
		type: 'contact'
	},

    items: [{
    	xtype: 'form',
    	reference: 'addContactForm',
    	bodyPadding: 10,
    	autoScroll: true,
    	controller: 'contactgroup',
    	
    	fieldDefaults: {
    		labelAlign: 'right',
    		labelWidth: 115
    	},
    	
    	defaultType: 'textfield',
    	
    	defaults: {
    		anchor: '100%',
			enableKeyEvents:true,
			listeners: {
				specialKey: 'submitOnEnter'
			}
    	},

    	items: [{
			fieldLabel: 'Firstname',
			allowBlank: false,
			bind: '{contact.firstname}'
		},{
			fieldLabel: 'Lastname',
			allowBlank: false,
			bind: '{contact.name}'
		},{
			fieldLabel: 'Phone number',
			allowBlank: false,
			bind: '{contact.phone_number}',
			vtype: 'phone'
		},{
			fieldLabel: 'Email',
			allowBlank: true,
			bind: '{contact.email}',
			vtype: 'email'
		},{
			fieldLabel: 'Description',
			allowBlank: true,
			bind: '{contact.description}'
		}],
    	
    	buttons: [{
			text: 'Create',
			formBind: true,
			reference: 'submitButton',
			listeners: {
				click: 'onCreateContactWindow'
			}
    	}]
    }]
});