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
Ext.define('JanuaWeb.view.action.ContactNotifyGrid', {
    extend: 'Ext.grid.Panel',

    alias: 'widget.ContactNotifyGrid',

    requires: [
        'JanuaWeb.view.action.ActionViewModel'
    ],
    
    controller: 'action',
    
    viewModel : {
        type: 'action'
    },
    
    listeners: {
        close: 'onCloseContactNotifyWindow',
        scope: 'controller'
    },

    width: 300,
    minHeight: 350,
    height: 350,

    resizable: false,
    modal: true,
    floating: true,
    closable: true,
    draggable: true,
    frame: true,

    autoShow: true,
    autoScroll: true,
    
    layout: 'fit',

    store: 'ContactNotifyGroup',

    viewConfig: {
        deferEmptyText: false,
        emptyText: 'No contacts, you should authorized group first'
    },
    selModel: {
        selType: 'checkboxmodel',
        showHeaderCheckbox: false,
        checkOnly: true
    },
    features: [{
        id: 'group',
        ftype: 'grouping',
        groupHeaderTpl: '{name}',
        hideGroupedHeader: true,
        enableGroupingMenu: false
    }],

    columns: [{
        text: 'Contacts',
        flex: 1,
        tdCls: 'task',
        sortable: true,
        dataIndex: 'contact',
        hideable: false
    },{
        header: 'Group',
        width: 180,
        sortable: true,
        dataIndex: 'group'
    }],

    buttons: [{
        text: 'Save',
        listeners: {
            click: 'onSaveContactNotifyWindow'
        }
    }]
});
