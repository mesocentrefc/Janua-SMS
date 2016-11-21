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
Ext.define('JanuaWeb.Application', {
    extend: 'Ext.app.Application',
    
    name: 'JanuaWeb',

    controllers: [
        'Start@JanuaWeb.controller'
    ],
    
    stores: [
        'RestProxy',
        'RestProxyFilter',
        'Languages',
        'Admin',
        'Sms',
        'Contact',
        'Group',
        'ContactGroup',
        'AdminLevel',
        'Action',
        'Supervisor',
        'AuthorizedGroupAction',
        'AuthorizedSupervisorAction',
        'ContactNotifyAction',
        'ContactNotifyFilter',
        'QuotaUnit',
        'SmsShortLog',
        'SmsStats',
        'AuthBackend',
        'AuthConfig',
        'ContactNotifyGroup'
    ],
    
    launch: function () {
        Ext.apply(Ext.form.field.VTypes, {
            password : function(val, field) {
                if (field.initialPassField) {
                    var pwd = Ext.getCmp(field.initialPassField);
                    return (val == pwd.getValue());
                }
                return true;
            },
            passwordText : 'Passwords do not match'
        });
        var phoneTest = /\+[0-9]+$/i;
        Ext.apply(Ext.form.field.VTypes, {
            phone: function(v) {
                return phoneTest.test(v);
            },
            phoneText: 'Must be in international format (ex: +33623457891)',
            phoneMask: /[\d\+]/i
        });
        var groupTest = /[a-zA-Z0-9-]+$/i;
        Ext.apply(Ext.form.field.VTypes, {
            group: function(v) {
                return groupTest.test(v);
            },
            groupText: 'Accented special characters are forbidden, except hyphen',
            groupMask: /[a-aA-Z0-9-]/i
        });
        Ext.data.StoreManager.lookup('QuotaUnit').each(function(rec) {
            JanuaWeb.Application.quotaUnit[rec.id] = rec.data.name;
        });
    },

    statics: {
        authConfigModels: new Ext.util.HashMap(),
        authConfigFormFields: new Ext.util.HashMap(),
        quotaUnit: new Array(),
        saveUs: function(config, store, pid) {
            var me = this;
            var manyStore = Ext.data.StoreManager.lookup(config.manyStore);
            var manyModel = config.manyModel;
            var primaryKey = config.primaryKey;
            var secondaryKey = config.secondaryKey;
            var successMessage = config.successMessage;
            var failureMessage = config.failureMessage;
            var reloadStores = [];

            if (config.reloadStores) {
                if (Ext.typeOf(config.reloadStores) == 'string') {
                    reloadStores.push(config.reloadStores);
                } else if (Ext.typeOf(config.reloadStores) == 'array') {
                    Ext.Array.each(config.reloadStores, function(store) {
                        reloadStores.push(store);
                    });
                } else {
                    console.error('[E] reloadStores has unknown type, only string or array are valid types');
                    return;
                }
            }
            reloadStores.push(manyStore);

            Ext.each(store.getNewRecords(), function(rec) {
                model_rec = {};
                model_rec[secondaryKey] = rec.id;
                model_rec[primaryKey] = pid;
                model = Ext.create(manyModel, model_rec);
                manyStore.add(model);
            });
            Ext.each(store.getRemovedRecords(), function(rec) {
                manyStore.filter([
                    {property: secondaryKey, value: rec.id},
                    {property: primaryKey, value: pid}
                ]);
                manyStore.each(function(rec) {
                    manyStore.remove(rec);
                });
                manyStore.clearFilter();
            });
            manyStore.sync({
                success: function() {
                    me.toastMe(config.successMessage);
                    store.commitChanges();
                    Ext.Array.each(reloadStores, function(storeName) {
                        Ext.data.StoreManager.lookup(storeName).reload();
                    });
                },
                failure: function() {
                    me.errorBox(config.failureMessage);
                    store.rejectChanges();
                    manyStore.reload();
                }
            });
        },

        toastMe: function(html) {
            Ext.toast({
                html: '<b>' + html + '</b>',
                closeOnMouseDown: true,
                closable: false,
                align: 't',
                autoCloseDelay: 1600,
                slideInDuration: 800,
                bodyPadding: 5
            });
        },

        confirmBox: function(title, fn, scope) {
            Ext.Msg.confirm(title, 'Are you sure ?', fn, scope);
        },

        warningBox: function(title, message, fn, scope) {
            Ext.Msg.show({
                title: title,
                message: message,
                buttons: Ext.Msg.YESNO,
                icon: Ext.Msg.WARNING,
                callback: fn,
                scope: scope
            });
        },

        infoBox: function(title, message) {
            Ext.Msg.show({
                title: title,
                message: message,
                buttons: Ext.Msg.OK,
                icon: Ext.Msg.INFO
            });
        },

        errorBox: function(message, operation) {
            var msg = "";
            if (operation) {
                data = Ext.decode(operation.error.response.responseText);
                if (message != '')
                    msg = message + ': ' + data['message'];
                else
                    msg = data['message'];
            } else {
                msg = message;
            }
            Ext.Msg.show({
                title: 'Error',
                message: msg,
                buttons: Ext.Msg.OK,
                icon: Ext.Msg.ERROR
            });
        },

        Base64: (function() {
            // Private property
            var keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    
            // Private method for UTF-8 encoding
            function utf8Encode(string) {
                string = string.replace(/\r\n/g,"\n");
                var utftext = "";
                for (var n = 0; n < string.length; n++) {
                    var c = string.charCodeAt(n);
                    if (c < 128) {
                        utftext += String.fromCharCode(c);
                    }
                    else if((c > 127) && (c < 2048)) {
                        utftext += String.fromCharCode((c >> 6) | 192);
                        utftext += String.fromCharCode((c & 63) | 128);
                    }
                    else {
                        utftext += String.fromCharCode((c >> 12) | 224);
                        utftext += String.fromCharCode(((c >> 6) & 63) | 128);
                        utftext += String.fromCharCode((c & 63) | 128);
                    }
                }
                return utftext;
            }
    
            // Public method for encoding
            return {
                encode : (typeof btoa == 'function') ? function(input) { return btoa(input); } : function (input) {
                    var output = "";
                    var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
                    var i = 0;
                    input = utf8Encode(input);
                    while (i < input.length) {
                        chr1 = input.charCodeAt(i++);
                        chr2 = input.charCodeAt(i++);
                        chr3 = input.charCodeAt(i++);
                        enc1 = chr1 >> 2;
                        enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
                        enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
                        enc4 = chr3 & 63;
                        if (isNaN(chr2)) {
                            enc3 = enc4 = 64;
                        } else if (isNaN(chr3)) {
                            enc4 = 64;
                        }
                        output = output +
                        keyStr.charAt(enc1) + keyStr.charAt(enc2) +
                        keyStr.charAt(enc3) + keyStr.charAt(enc4);
                    }
                    return output;
                }
            };
        })()
    }
});
