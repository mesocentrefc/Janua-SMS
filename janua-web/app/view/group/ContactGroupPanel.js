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
Ext.define('JanuaWeb.view.group.ContactGroupPanel', {
    extend: 'Ext.panel.Panel',
    xtype: 'contact-group-panel',
    alias: 'widget.ContactGroupPanel',
    
    requires: [
        'JanuaWeb.view.group.ContactGroupController',
        'JanuaWeb.view.group.GroupGrid',
        'JanuaWeb.view.group.ContactGrid'
    ],
    
    controller: 'contactgroup',
    reference: 'contactgroupPanel',

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

	bodyPadding: 5,

    items: [{
    	title: 'Groups',
    	xtype: 'GroupGrid',
		frame: true,
		flex: 1
    },{
    	title: 'Contacts',
    	xtype: 'ContactGrid',
		frame: true,
		margin: '5 0 0 0',
		flex: 1
    }]
});