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
Ext.define('JanuaWeb.view.group.AddGroupWindow', {
    extend: 'Ext.window.Window',
    xtype: 'AddGroupWindow',

    controller: 'contactgroup',

    title: 'Add a new group',
    resizable: false,
    modal: true,
    layout: 'fit',

    autoShow: true,
    autoScroll: true,

	viewModel : {
		type: 'contact'
	},

    items: [{
    	xtype: 'form',
    	bodyPadding: 10,
    	autoScroll: true,
		referenceHolder: true,

    	fieldDefaults: {
    		labelAlign: 'left',
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
    	    fieldLabel: 'Group name', 
    	    name: 'name',
			allowBlank: false,
			bind: '{group.name}',
			vtype: 'group'
    	},{
			fieldLabel: 'Description',
			allowBlank: true,
			bind: '{group.description}'
		}],

    	buttons: [{
			text: 'Create',
			formBind: true,
			reference: 'submitButton',
			listeners: {
				click: 'onCreateGroupWindow'
			}
    	}]
    }]
});