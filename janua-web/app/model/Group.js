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
Ext.define('JanuaWeb.model.Group', {
	extend: 'JanuaWeb.model.Base',

	fields: [
	    {name: 'name'},
		{name: 'description'}
	],

	manyToMany: {
		ContactGroups: {
			type: 'ContactGroup',
			role: 'contacts',
			field: 'contact_id',
			right: {
				field: 'group_id'
			}
		}
	},
	proxy: {
	    url: 'api/GROUPS'
	}
})