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
Ext.define('JanuaWeb.model.Admin', {
	extend: 'JanuaWeb.model.Base',
	
	fields: [
	    {name: 'login'},
	    {name: 'name'},
	    {name: 'firstname'},
	    {name: 'phone_number'},
	    {name: 'has_client', type: 'boolean', defaultValue: false},
	    {name: 'password'},
	    {name: 'email'},
	    {name: 'level', type: 'integer'},
		{name: 'sms_quota'},
		{name: 'recipient_filter', type: 'boolean', defaultValue: true},
		{name: 'auth_backend'},
		{name: 'fullname'},
		{
			name: 'display',
			persist: false,
			convert: function(v, rec) {
				return rec.data.firstname + " " + rec.data.name;
			}
		},
		{
			name: 'quota_limit',
			persist: false,
			convert: function(v, rec) {
				return Ext.String.splitWords(rec.data.sms_quota)[0];
			}
		},
		{
			name: 'quota_unit',
			persist: false,
			convert: function(v, rec) {
				return Ext.String.splitWords(rec.data.sms_quota)[1];
			}
		}
	],

	proxy: {
        url: 'api/ADMIN'
    }
})