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
Ext.define('JanuaWeb.view.message.MessageStatsGraph', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.MessageStatsGraph',

    layout: 'fit',
    bodyPadding: 5,
    items: [{
        xtype: 'chart',
        margin: '5 0 0 0',
        animate: true,
        shadow: false,
        store: 'SmsStats',
        axes: [{
            type: 'numeric',
            position: 'left',
            grid: true,
            fields: 'value',
            minimum: 0
        }, {
            type: 'category',
            position: 'bottom',
            fields: 'month'
        }],
        series: [{
            type: 'bar',
            axis: 'left',
            xField: 'month',
            yField: 'value',
            style: {
                opacity: 0.70
            },
            highlight: {
                fillStyle: 'yellow',
                radius: 5,
                linewidth: 1
            },
            tips: {
                trackMouse: true,
                renderer: function(tooltip, storeItem, item) {
                    tooltip.setHtml(storeItem.get('month') + ': ' + storeItem.get('value') + ' SMS sent');
                }
            }
        }]
    }]
});
