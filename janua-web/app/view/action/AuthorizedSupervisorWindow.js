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
Ext.define('JanuaWeb.view.action.AuthorizedSupervisorWindow', {
    extend: 'Ext.window.Window',

    xtype: 'AuthorizedSupervisorWindow',

    requires: [
        'JanuaWeb.view.action.ActionViewModel',
        'Ext.view.MultiSelector'
    ],
    
    controller: 'action',
    
    viewModel : {
        type: 'action'
    },
    
    listeners: {
        close: 'onCloseAuthorizedSupervisorWindow',
        scope: 'controller'
    },

    bind: 'Supervisor authorization for action {action.name}',

    width: 300,
    minHeight: 250,
    height: 300,
    bodyPadding: 5,
    
    autoShow: true,
    autoScroll: true,

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    modal: true,
    
    items: [{
        xtype: 'component',
        html: 'Select supervisor authorized to trigger this action',
        margin: 0
    },{
        xtype: 'multiselector',
        bind: '{action.authorized_supervisor}',

        fieldName: 'fullname',

        viewConfig: {
            deferEmptyText: false,
            emptyText: 'No supervisor selected'
        },

        removeRowTip: 'Remove this supervisor',
        addToolText: 'Search for supervisors to add',

        title: 'Authorized supervisors',
        flex: 1,
        margin: '5 0',
        search: {
            closeAction: 'hide',
            closable: true,
            title: 'Supervisor selection',
            height: 300,
            store: {
                model: 'Supervisor',
                pageSize: 0
            }
        }
    }],

    buttons: [{
        text: 'Save',
        formBind: true,
        listeners: {
            click: 'onSaveAuthorizedSupervisorWindow'
        }
    }]
});