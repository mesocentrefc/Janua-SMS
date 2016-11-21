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
Ext.define('JanuaWeb.view.main.HomePanel', {
    extend: 'Ext.panel.Panel',
    xtype: 'home-panel',
    alias: 'widget.HomePanel',
    
    controller: 'main',

    layout: {
        type: 'vbox',
        align: 'center'
    },

    autoScroll: true,
    items: [{
        padding: '40 0 20 0',
        html: '<b>Janua-SMS gateway</b>',
        xtype: "box"
    },{
        html: '<b>Features</b><br/>'+
        '- Multi-user support<br/>' +
        '- Groups and contacts management<br/>' +
        '- Send individual or group SMS/MAIL<br/>' +
        '- Trigger action on received SMS<br/>' +
        '- Highly customizable (authentication plugins, custom actions)<br/>',
        padding: '0 0 20 0',
        xtype: 'box'
    },{
        layout: {
            type: 'hbox',
            align: 'center'
        },
        items: [{
            xtype: 'image',
            mode: '',
            src: 'resources/meso_logo.png',
            alt: 'meso_logo',
            imgCls: 'meso_logo',
            autoEl: {
                tag: 'a',
                href: 'http://meso.univ-fcomte.fr',
                target: '_blank'
            }
        },{
            padding: '0 0 0 50',
            xtype: 'image',
            src: 'resources/UFC_logo.png',
            alt: 'ufc_logo',
            imgCls: 'ufc_logo',
            autoEl: {
                tag: 'a',
                href: 'http://www.univ-fcomte.fr',
                target: '_blank'
            }
        }]
    },{
        padding: 20,
        xtype: 'box',
    }]
});
