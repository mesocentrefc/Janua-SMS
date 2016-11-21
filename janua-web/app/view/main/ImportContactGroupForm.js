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
Ext.define('JanuaWeb.view.main.ImportContactGroupForm', {
    extend: 'Ext.form.Panel',

    xtype: 'ImportContactGroupForm',
    
    requires: [
        'Ext.form.field.File'
    ],

    controller: 'main',

    resizable: false,
    modal: true,
    floating: true,
    closable: true,
    frame: true,
    
    layout: 'anchor',

    autoShow: true,
    autoScroll: false,

    title: 'Import contacts and group from CSV file',
    width: 400,
    bodyPadding: 10,
    
    listeners: {
        afterrender: 'onDisplayImportForm'
    },

    items: [{
        xtype: 'filefield',
        reference: 'csvfileImportField',
        name: 'csvfile',
        fieldLabel: 'CSV file',
        labelWidth: 60,
        msgTarget: 'side',
        allowBlank: false,
        anchor: '100%',
        buttonText: 'Select file...'
    }],

    dockedItems: [{
        xtype: 'statusbar',
        defaultText: 'Ready',
        reference: 'sbState',
        dock: 'bottom',
        ui: 'footer',
        items: ['->', {
            xtype: 'button',
            text: 'Import',
            formBind: true,
            listeners: {
                click: 'onImportContactGroupForm'
            }
        }]
    }]
});
