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
Ext.define('JanuaWeb.view.action.ManagedByWindow', {
    extend: 'Ext.window.Window',

    xtype: 'ManagedByWindow',

    requires: [
        'JanuaWeb.view.action.ActionViewModel'
    ],
    
    controller: 'action',
    
    viewModel : {
        type: 'action'
    },

    bind: 'Action {action.name} manager',

    resizable: false,
    modal: true,
    layout: 'fit',
    
    autoShow: true,
    autoScroll: true,

    items: [{
        xtype: 'form',
        bodyPadding: 10,
        autoScroll: true,
        
        fieldDefaults: {
            labelAlign: 'left',
            labelWidth: 115
        },

        defaults: {
            anchor: '100%'
        },

        items: [{
            fieldLabel: 'Administrator',
            xtype: 'combobox',
            editable: false,
            forceSelection: true,
            displayField: 'display',
            autoLoadOnValue: true,
            reference: 'comboAdmin',
            valueField: 'display',
            bind: {
                store: '{Admins}',
                value: {
                    bindTo: '{action.admin.display}'
                }
            }
        }],

        buttons: [{
            text: 'Save',
            formBind: true,
            listeners: {
                click: 'onSaveManagedByWindow'
            }
        }]
    }]
});
