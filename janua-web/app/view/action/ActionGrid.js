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
Ext.define('JanuaWeb.view.action.ActionGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.ActionGrid',

    controller: 'action',

    stateful: true,

    store: 'Action',

    reference: 'actionGrid',

    dockedItems: [{
        xtype: 'pagingtoolbar',
        store: 'Action',
        dock: 'top',
        displayInfo: true
    }],

    columns: [{
        dataIndex: 'name',
        text: 'Name',
        flex: 1
    },{
        dataIndex: 'description',
        text: 'Description',
        flex: 2
    },{
        xtype: 'booleancolumn',
        dataIndex: 'authentication',
        text: 'Authentication required',
        falseText: 'No',
        trueText: 'Yes',
        flex: 1
    },{
        xtype: 'booleancolumn',
        dataIndex: 'enabled',
        text: 'Enabled',
        falseText: 'No',
        trueText: 'Yes',
        flex: 1
    },{
        dataIndex: 'managed_by',
        text: 'Managed by',
        flex: 1
    },{
        xtype: 'widgetcolumn',
        text: 'AUTHORIZED',
        width: 100,
        widget: {
            xtype: 'button',
            text: 'GROUP',
            handler: 'onAuthorizedGroupClick'
        },
        onWidgetAttach: function(widget, e, rec) {
            if (Ext.util.Cookies.get("admin_id") != rec.get('admin_id') || rec.get('authentication') == true) {
                e.hide();
            } else {
                e.show();
            }
        }
    },{
        xtype: 'widgetcolumn',
        text: 'NOTIFY',
        width: 100,
        widget: {
            xtype: 'button',
            text: 'CONTACT',
            handler: 'onContactNotifyClick'
        },
        onWidgetAttach: function(widget, e, rec) {
            if (Ext.util.Cookies.get("admin_id") != rec.get('admin_id') || rec.get('authentication') == true) {
                e.hide();
            } else {
                e.show();
            }
        }
    },{
        xtype: 'widgetcolumn',
        text: 'AUTHORIZED',
        width: 130,
        reference: 'widgetSupervisor',
        widget: {
            xtype: 'button',
            text: 'SUPERVISOR',
            handler: 'onAuthorizedSupervisorClick'
        },
        onWidgetAttach: function(widget, e, rec) {
            if (Ext.util.Cookies.get("role") != 'admin') {
                e.hide();
            } else {
                e.show();
            }
        }
    },{
        xtype: 'widgetcolumn',
        text: 'ACTION',
        width: 130,
        reference: 'widgetManagedBy',
        widget: {
            xtype: 'button',
            text: 'MANAGED BY',
            handler: 'onManagedByClick'
        },
        onWidgetAttach: function(widget, e, rec) {
            if (Ext.util.Cookies.get("role") != 'admin' || rec.get('authentication') == true) {
                e.hide();
            } else {
                e.show();
            }
        }
    }],
    listeners: {
        add: function(me, component, index, eOpts) {
            if (Ext.util.Cookies.get("role") != 'admin') {
                Ext.each(component.grid.columns, function(col) {
                    if (Ext.Array.contains(['widgetSupervisor', 'widgetManagedBy'], col.reference))
                        col.setVisible(false);
                });
            }
        }
    }
})
