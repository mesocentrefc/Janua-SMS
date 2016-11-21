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
Ext.define('JanuaWeb.view.main.AuthConfigForm', {
    extend: 'Ext.form.Panel',

    xtype: 'AuthConfigForm',
    
    controller: 'main',

    viewModel: {
        type: 'main'
    },

    listeners: {
        close: 'onCloseAuthConfigForm',
        scope: 'controller'
    },

    resizable: false,
    modal: true,
    floating: true,
    closable: true,
    draggable: true,
    frame: true,

    layout: 'anchor',

    autoShow: false,
    autoScroll: false,

    fieldDefaults: {
        labelAlign: 'right',
        labelWidth: 120,
        anchor: '100%'
    },
        
    title: 'Configure {0} authentication backend',
    width: 500,
    bodyPadding: 8,

    tools: [{
        type: 'help',
        hidden: true,
        tooltip: 'Configuration help',
        handler: 'onAuthConfigHelpClick',
        reference: 'AuthConfigHelpButton'
    }],

    buttons: [{
        text: 'Save',
        formBind: true,
        handler: 'onAuthSaveConfig'
    }],

    constructor: function(config) {
        var me = this;
        config.items = JanuaWeb.Application.authConfigFormFields.get(config.backend);
        this.callParent([config]);
        me.setTitle(Ext.String.format(me.getTitle(), config.backend));
    }
});
