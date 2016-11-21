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
Ext.define('JanuaWeb.model.Action', {
    extend: 'JanuaWeb.model.Base',

    fields: [
        {name: 'name'},
        {name: 'description'},
        {name: 'authentication', type: 'boolean'},
        {name: 'enabled', type: 'boolean'},
        {name: 'admin_id', type: 'integer', reference: 'Admin'},
        {
            name: 'managed_by',
            persist: 'false',
            convert: function(v, rec) {
                if (rec.data.admin)
                    return rec.data.admin.firstname + ' ' + rec.data.admin.name;
                else
                    return;
            }
        }
    ],

    manyToMany: {
        AuthorizedGroup: {
            type: 'AuthorizedGroupAction',
            role: 'authorized_group',
            field: 'group_id',
            right: {
                field: 'action_id'
            }
        },
        AuthorizedSupervisor: {
            type: 'AuthorizedSupervisorAction',
            role: 'authorized_supervisor',
            field: 'admin_id',
            right: {
                field: 'action_id'
            }
        },
        ContactNotify: {
            type: 'ContactNotifyAction',
            role: 'contact_notify',
            field: 'contact_id',
            right: {
                field: 'action_id'
            }
        }
    },

    proxy: {
        url: 'api/ACTION'
    }
})