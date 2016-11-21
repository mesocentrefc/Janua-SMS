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
Ext.define('JanuaWeb.view.login.LoginController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.login',

    requires: [
        'Ext.window.Toast'
    ],  

    loginText: 'Logging in...',

    constructor: function () {
        this.callParent(arguments);

        this.loginManager = new JanuaWeb.LoginManager({
            session: this.session
        });
    },
    
    onLoginClick: function(me, e) {
        this.doLogin();
    },
    
    doLogin: function() {
        var form = Ext.getCmp('login-form').form;

        if (form.isValid()) {
            Ext.getBody().mask(this.loginText);
            
            this.loginManager.login({
                data: form.getValues(),
                scope: this,
                success: 'onLoginSuccess',
                failure: 'onLoginFailure'
            });
        }
    },

    onLoginFailure: function(message, loginform) {
        Ext.getBody().unmask();
        Ext.toast({
            title: 'Login failed',
            html: '<b>' + message + '</b>',
            closeOnMouseDown: true,
            closable: false,
            align: 't',
            autoCloseDelay: 1600,
            slideInDuration: 800,
            bodyPadding: 5
        });
    },

    onLoginSuccess: function(options) {
        Ext.getBody().unmask();
        this.fireViewEvent('login', this.getView(), this.loginManager);
    }
});
