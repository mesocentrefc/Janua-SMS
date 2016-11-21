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
Ext.define('JanuaWeb.store.RestProxyFilter', {
    extend: 'JanuaWeb.store.RestProxy',
    alias: 'proxy.RestProxyFilter',

    buildUrl: function(request) {
        var q = new Object ();
        var params = request.getParams();
        
        if ("sort" in params) {
            var sort = Ext.JSON.decode(params['sort']);
            q["order_by"] = Ext.JSON.decode('[{"field":"'+sort[0]["property"]+'","direction":"'+Ext.util.Format.lowercase(sort[0]["direction"])+'"}]');    
            delete(params["sort"]);
        }
        if ("filter" in params) {
            var filter = Ext.JSON.decode(params['filter']);
            if (filter[0]["property"] == 'filter' && filter[0]["value"] != undefined) {
               q["filters"] = filter[0]["value"];
               delete(params["filter"]);
            }
        }
        if (Object.keys(q).length != 0) {
            params["q"] = Ext.JSON.encode(q);    
        }
        return this.callParent([request]);
    }
});