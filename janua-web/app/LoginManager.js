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
Ext.define('JanuaWeb.LoginManager', {
    config: {
        model: null,
        session: null
    },

    constructor: function (config) {
        this.initConfig(config);
    },

    applyModel: function(model) {
        return model && Ext.data.schema.Schema.lookupEntity(model);
    },

    login: function(options) {
        var conn = new Ext.data.Connection();
        conn.request({
            url: '/login',
            method: 'POST',
            params: Ext.JSON.encode(options.data),
            scope: this,
            callback: this.onLoginReturn,
            original: options,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    },

    onLoginReturn: function(options, success, response) {
        options = options.original;
        var session = this.getSession();

        if (success) {
            JSONresponse = Ext.JSON.decode(response.responseText);
            if (JSONresponse.success) {
                Ext.callback(options.success, options.scope, [options]);
                return;
            } else {
                Ext.callback(options.failure, options.scope, [JSONresponse.message]);
                return;
            }
        } else {
            Ext.callback(options.failure, options.scope, ['Bad or no response from server']);
        }
    }

});
