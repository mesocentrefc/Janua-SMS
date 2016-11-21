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
Ext.define('JanuaWeb.controller.Start', {
    extend: 'Ext.app.Controller',
    
    requires: [
        'JanuaWeb.view.login.Login',
        'JanuaWeb.view.main.Main',
        'JanuaWeb.LoginManager',
        'JanuaWeb.view.action.ActionGrid'
    ],

    loadingText: 'Loading...',

    onLaunch: function () {
        if (Ext.isIE8) {
            Ext.Msg.alert(
                'Not Supported',
                'This site is not supported on Internet Explorer 8.' +
                ' Please use a different browser.'
            );
            return;
        }
        var session = this.session = new Ext.data.Session();

        // check cookie session (not for security heh !)
        var admin_id = Ext.util.Cookies.get("admin_id");
        if (admin_id) {
            this.showUI();
        } else {
            this.login = new JanuaWeb.view.login.Login({
                session: session,
                autoShow: true,
                listeners: {
                    scope: this,
                    login: 'onLogin'
                }
            });
            this.login.render(Ext.getBody());
            this.login.center();
        }
    },

    /**
     * Called when the login controller fires the "login" event.
     *
     * @param loginController
     * @param loginManager
     */
    onLogin: function (loginController, loginManager) {
        this.login.destroy();

        this.loginManager = loginManager;
        if (Ext.isChrome) {
            document.location.href = 'index.html';
        } else {
            this.showUI();
        }
    },
    
    showUI: function() {
        var me = this;
        var role = Ext.util.Cookies.get("role");
        var runner = new Ext.util.TaskRunner();
        var task;

        Ext.Ajax.setDefaultHeaders({
            'JanuaAuthToken': Ext.util.Cookies.get("auth_token")
        });

        Ext.data.StoreManager.lookup("ContactGroup").load();
        Ext.data.StoreManager.lookup("Contact").load();
        Ext.data.StoreManager.lookup("Group").load();
        Ext.data.StoreManager.lookup("Admin").load();
        Ext.data.StoreManager.lookup("Action").load();
        Ext.data.StoreManager.lookup("AuthorizedGroupAction").load();
        Ext.data.StoreManager.lookup("ContactNotifyAction").load();
        Ext.data.StoreManager.lookup("Sms").load();
        Ext.data.StoreManager.lookup("SmsShortLog").load();
        Ext.data.StoreManager.lookup("SmsStats").load();

        this.viewport = new JanuaWeb.view.main.Main({
            session: this.session
        });

        var tabpanel = this.viewport.lookupReference('mainTab');
        if (role == 'supervisor') {
            tabpanel.remove(this.viewport.lookupReference('adminPanel'), false);
            action_panel = this.viewport.lookupReference('actionPanel');
            tabpanel.remove(action_panel, false);
            item = {
                title: 'Action ACLs',
                xtype: 'ActionGrid',
                frame: true,
                margin: '5 0 0 0',
                flex: 1
            }
            this.viewport.lookupReference('supervisorPanel').add(item);

            menu = this.viewport.lookupReference('authenticationMenu');
            menu.hide();
        } else {
            myaccount_menu = this.viewport.lookupReference('MyAccountMenu');
            smsquota_menu = myaccount_menu.lookupReference('SmsQuotaMenu');
            smsquota_menu.setDisabled(true);

            Ext.data.StoreManager.lookup("AuthBackend").load({
                callback: function(records, options, success) {
                    if (success == true) {
                        menu = me.viewport.lookupReference('authenticationMenu').menu;
                        Ext.each(records, function(rec) {
                            backend = rec.getData();
                            if (backend.name != 'local') {
                                menu.add({
                                    text: 'Configure ' + backend.name,
                                    name: backend.name,
                                    handler: 'onAuthConfig'
                                });
                                store = new JanuaWeb.store.AuthConfig();
                                store.getProxy().setUrl('/get_auth_backend/' + backend.name);
                                store.load({
                                    callback: function(records, options, success) {
                                        if (success == true) {
                                            modelfields = [];
                                            formfields = [];
                                            Ext.each(records[0].get('params'), function(param) {
                                                modelfields.push({
                                                    name: param.name,
                                                    type: param.type,
                                                    defaultValue: param.value
                                                });
                                                if (param.type == 'string') {
                                                    formfields.push({
                                                        xtype: 'textfield',
                                                        name      : param.name,
                                                        fieldLabel: param.description,
                                                        bind: Ext.String.format('{backend.{0}}', param.name),
                                                        allowBlank: false
                                                    })
                                                } else if (param.type == 'boolean') {
                                                    formfields.push({
                                                        name: param.name,
                                                        fieldLabel: param.description,
                                                        bind: Ext.String.format('{backend.{0}}', param.name),
                                                        xtype: 'checkbox',
                                                        checked: true,
                                                        inputValue: true,
                                                        uncheckedValue: false
                                                    })
                                                } else if (param.type == 'integer') {
                                                    formfields.push({
                                                        xtype: 'numberfield',
                                                        name      : param.name,
                                                        fieldLabel: param.description,
                                                        bind: Ext.String.format('{backend.{0}}', param.name),
                                                        allowBlank: false,
                                                        anchor: '50%'
                                                    })
                                                }
                                            });
                                            if (records[0].get('help')) {
                                                formfields.push({
                                                    xtype: 'component',
                                                    reference: 'helpAuthConfigMessage',
                                                    hidden: true,
                                                    html: '<hr>' + records[0].get('help'),
                                                    margin: 0
                                                });
                                            }
                                            tmpmodel = Ext.define('JanuaWeb.model.AuthConfig' + backend.name, {
                                                fields: modelfields,
                                                extend: 'Ext.data.Model',
                                                proxy: {
                                                    type: 'ajax',
                                                    url: '/set_auth_backend/' + backend.name,
                                                    reader: {
                                                        type: 'json',
                                                        rootProperty: 'backends',
                                                        totalProperty: 'num_backends'
                                                    },
                                                    writer: {
                                                        type: 'json',
                                                        rootProperty: 'parameters',
                                                        writeRecordId: false,
                                                        writeAllFields: false
                                                    }
                                                }
                                            });
                                            JanuaWeb.Application.authConfigModels.add(backend.name, new tmpmodel());
                                            JanuaWeb.Application.authConfigFormFields.add(backend.name, formfields);
                                        }
                                    }
                                });
                            }
                        })
                    }
                }
            });
            tabpanel.remove(this.viewport.lookupReference('supervisorPanel'), false);
            Ext.data.StoreManager.lookup("AuthorizedSupervisorAction").load();
            
        }

        task = {
            run: this.checkUserSession,
            scope: this,
            interval: 60000
        };
        runner.start(task);
    },

    getSession: function() {
        return this.session;
    },

    checkUserSession: function() {
        var smsusage = this.viewport.lookupReference('smsUsage');
        var conn = new Ext.data.Connection();

        conn.request({
            url: 'sms-usage',
            success: function(resp, opt) {
                var data = Ext.decode(resp.responseText);
                var sent = data.smsusage.sent;
                var sms_quota = Ext.String.splitWords(data.smsusage.quota);
                var limit = sms_quota[0];
                var unit = JanuaWeb.Application.quotaUnit[sms_quota[1]];
                var value = "";
                if ('global' in data.smsusage) {
                    value += "Global month usage: " + data.smsusage.global + " SMS | ";
                }
                value += "My SMS usage: " + sent + " / " + limit + " per " + unit;
                smsusage.setValue(value);
            },
            failure: function(resp, opt) {
                if (resp.status == 401) {
                    Ext.Msg.show({
                        title: 'Check session',
                        msg: 'Your session has expired',
                        buttons: Ext.Msg.OK,
                        icon: Ext.Msg.ERROR,
                        fn: function(btn) {
                            location.href = 'logout';
                        }
                    });
                }
                if (resp.status == 503) {
                    Ext.Msg.show({
                        title: 'Check session',
                        msg: 'Server not responding',
                        buttons: Ext.Msg.OK,
                        icon: Ext.Msg.ERROR
                    });
                }
            },
            headers: {
                'JanuaAuthToken': Ext.util.Cookies.get("auth_token")
            }
        });
    }
});
