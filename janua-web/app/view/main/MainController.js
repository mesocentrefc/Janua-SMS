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
Ext.define('JanuaWeb.view.main.MainController', {
    extend: 'Ext.app.ViewController',

    requires: [
        'Ext.window.MessageBox',
        'JanuaWeb.view.main.ImportContactGroupForm',
        'JanuaWeb.view.main.AuthConfigForm',
        'JanuaWeb.view.main.RequestQuotaForm'
    ],
    
    alias: 'controller.main',
    
    onLogout: function () {
        Ext.Msg.confirm('Logout', 'Are you sure ?', 'onLogoutConfirm', this);
    },

    onLogoutConfirm: function (choice) {
        if (choice === 'yes') {
            document.location.href = "logout";
        }
    },

    onDisplayImportForm: function() {
        var tab = this.lookupReference('mainTab');
    //    tab.setActiveTab(2);
    },

    onImportContactGroupForm: function() {
        var me = this;
        var field = me.lookupReference('csvfileImportField');
        var file = field.fileInputEl.dom.files[0];
        var reader = new FileReader();
        reader.onload = (function(theFile) {
            return function(e) {
                me.importCSVFile(me, e.target.result);
            };
        })(file);
        reader.onerror = (function(theFile) {
            return function(e) {
                console.error("BAD FILE");
            };
        });
        reader.readAsText(file);
    },

    onImportContactGroup: function() {
        var widget = Ext.widget('ImportContactGroupForm');
    },

    onExportContactGroup: function() {
        var contactStore = Ext.data.StoreManager.lookup('Contact');
        var groupStore = Ext.data.StoreManager.lookup('Group');
        var contactgroupStore = Ext.data.StoreManager.lookup('ContactGroup');
        var newline = "\r\n";
        var csvfile = "";

        csvfile += "FIRSTNAME,NAME,PHONE,EMAIL,DESCRIPTION,GROUPS" + newline;

        contactStore.each(function(rec) {
            var groups = [];
            var id = rec.get('id');
            firstname = rec.get('firstname');
            name = rec.get('name');
            email = rec.get('email');
            phone = '"' + rec.get('phone_number') + '"';
            description = rec.get('description');

            contactgroup = contactgroupStore.queryBy(function filter(record) {
                if (record.get('contact_id') == id) {
                    return true;
                }
            });
            contactgroup.each(function(rec) {
                groups.push(groupStore.findRecord('id', rec.get('group_id')).get('name'));
            });
            row = [firstname, name, phone, email, description, groups.join(':')];
            csvfile += row.join(',') + newline;
        });
        document.location = 'data:text/csv;charset=utf-8;base64,' + JanuaWeb.Application.Base64.encode(unescape(encodeURIComponent(csvfile)));
    },

    onSMSQuotaRequest: function() {
        var widget = Ext.widget('RequestQuotaForm');
        var requestView = widget.getViewModel();
        var adminStore = Ext.data.StoreManager.lookup('Admin');
        var record = adminStore.findRecord('id', Ext.util.Cookies.get("admin_id"));

        requestView.setData({admin: record});
    },

    onSendRequestQuota: function() {
        var me = this;
        var view = me.getView();
        quota_unit = view.lookupReference('quotaUnit');
        quota_limit = view.lookupReference('quotaLimit');

        admin = view.getViewModel().getData().admin;
        if (quota_limit.value != admin.get('quota_limit') || quota_unit.value != admin.get('quota_unit'))
            admin.set('sms_quota', quota_limit.value + " " + quota_unit.value);

        if (Ext.Object.getSize(admin.getChanges())) {
            admin.save({
                success: function(rec, op) {
                    JanuaWeb.Application.toastMe('Your request has been submitted to administrator');
                },
                failure: function(rec, op) {
                    JanuaWeb.Application.errorBox('', op);
                }
            });
        }
        this.closeWindow(view);
    },

    onSettings: function() {
        var widget = Ext.widget('EditSettingsWindow');
        var settingsView = widget.getViewModel();
        var adminStore = Ext.data.StoreManager.lookup('Admin');
        var record = adminStore.findRecord('id', Ext.util.Cookies.get("admin_id"));

        settingsView.setData({admin: record});
    },

    onCloseSettingsWindow: function() {
        var view = this.getView();
        var admin = view.getViewModel().getData().admin;
        
        admin.reject();

        this.closeWindow(view);
    },
    
    onSaveSettingsWindow: function() {
        var me = this;
        var view = this.getView();
        var pass1 = Ext.getCmp('myp1');
        var pass2 = Ext.getCmp('myp2');

        rec = view.getViewModel().getData().admin;
        if (pass1.value != '' && (pass1.value == pass2.value)) {
            rec.set('password', pass1.value);
        }
        if (pass1.value != '' && (pass1.value != pass2.value)) {
            JanuaWeb.Application.errorBox('Password confirmation doesn\'t match');
        } else {
            if (Ext.Object.getSize(rec.getChanges())) {
                rec.save({
                    success: function(rec, op) {
                        JanuaWeb.Application.toastMe('Changes has been applied');
                        me.fireEvent('updateAction');
                    },
                    failure: function(rec, op) {
                        JanuaWeb.Application.errorBox('', op);
                    }
                });
            }
            this.closeWindow(view);
        }
    },

    onChangePassword: function(me, newValue, oldValue, eOpts) {
        var pass1 = Ext.getCmp('myp1');
        var pass2 = Ext.getCmp('myp2');

        if (newValue == false) {
            pass1.setValue('');
            pass2.setValue('');
        }
    },

    onAuthConfig: function(btn, e) {
        var form = new JanuaWeb.view.main.AuthConfigForm({backend: btn.name});
        var settingsView = form.getViewModel();
        model = JanuaWeb.Application.authConfigModels.get(btn.name);
        settingsView.setData({backend: model});
        help = form.lookupReference('helpAuthConfigMessage');
        if (help) {
            form.tools[0].hidden = false;
        }
        form.show();
    },

    onAuthSaveConfig: function() {
        var me = this;
        var view = this.getView();

        rec = view.getViewModel().getData().backend;
        if (Ext.Object.getSize(rec.getChanges())) {
            rec.save({
                success: function(rec, op) {
                    var response = op.getResponse();
                    var data = Ext.decode(response.responseText);
                    JanuaWeb.Application.toastMe(data['message']);
                },
                failure: function(rec, op) {
                    JanuaWeb.Application.errorBox('', op);
                }
            });
        }
        this.closeWindow(view);
    },

    onCloseAuthConfigForm: function() {
        var view = this.getView();
        var backend = view.getViewModel().getData().backend;
        
        backend.reject();

        this.closeWindow(view);
    },

    onAuthConfigHelpClick: function() {
        var message = this.lookupReference('helpAuthConfigMessage');
        message.setHidden(!message.hidden);
    },

    privates: {
        closeWindow: function(view) {
            var action;

            if (view) {
                action = this.getCloseViewAction();
                view[action]();
            }
        },

        saveContactGroup: function(params) {
            var form = params.form;
            var contactGroupStore = params.contactGroupStore;
            var groupStore = params.groupStore;
            var contactStore = params.contactStore;
            var status = params.status;
            var countcontactgroup = params.countcontactgroup;
            var importedcontactgroup = params.importedcontactgroup;
            var view = params.view;
            var errors = params.errors;

            countc = countcontactgroup;
            importedcontactgroup.each(function(key, value, length) {
                group = groupStore.findRecord('name', key, false, false, true);
                groupid = group.get('id');
                for (i = 0; i < value.length; i++) {
                    contact = contactStore.findRecord('phone_number', value[i], false, false, true);
                    contactid = contact.get('id');
                    contactgroup = new JanuaWeb.model.ContactGroup({
                        'contact_id': contactid,
                        'group_id': groupid
                    });
                    contactgroup.save({
                        success: function(rec, operation) {
                            countc -= 1;
                            if (countc == 0) {
                                contactGroupStore.reload({
                                    callback: function(r, options, success) {
                                        form.unmask();
                                        view.close();
                                        if (success == true) {
                                            groupStore.reload();
                                            if (errors.length) {
                                                JanuaWeb.Application.errorBox(errors.join('<br/>'));
                                            } else {
                                                JanuaWeb.Application.toastMe('Contact and groups have been imported');
                                            }
                                        } else {
                                            JanuaWeb.Application.errorBox('Failed to refresh contact groups');
                                        }
                                    }
                                });
                            }
                        },
                        failure: function(rec, operation) {
                            countc -= 1;
                            contact_id = rec.get('contact_id');
                            group_id = rec.get('group_id');
                            contact = contactStore.findRecord('id', contact_id, false, false, true);
                            group = groupStore.findRecord('id', group_id, false, false, true);
                            errors.push('Failed to import contact ' +
                                        contact.get('firstname') + ' ' + contact.get('name') +
                                        ' in group ' + group.get('name'));
                            if (countc == 0) {
                                contactGroupStore.reload({
                                    callback: function(r, options, success) {
                                        form.unmask();
                                        view.close();
                                        if (success == true) {
                                            groupStore.reload();
                                            if (errors.length) {
                                                JanuaWeb.Application.errorBox(errors.join('<br/>'));
                                            } else {
                                                JanuaWeb.Application.toastMe('Contact and groups have been imported');
                                            }
                                        } else {
                                            JanuaWeb.Application.errorBox('Failed to refresh contact groups');
                                        }
                                    }
                                });
                            }
                        }
                    });
                }
            });
            importedcontactgroup.clear();
        },

        reloadAll: function(params) {
            var form = params.form;
            var contactGroupStore = params.contactGroupStore;
            var groupStore = params.groupStore;
            var contactStore = params.contactStore;
            var status = params.status;
            var countcontactgroup = params.countcontactgroup;
            var importedcontactgroup = params.importedcontactgroup;
            var me = params.scope;
            var view = params.view;
            var errors = params.errors;

            groupStore.reload({
                callback: function(r, options, success) {
                    if (success === true) {
                        contactStore.reload({
                            callback: function(r, options, success) {
                                if (success == true) {
                                    if (countcontactgroup)
                                        me.saveContactGroup(params);
                                } else {
                                    form.unmask();
                                    view.close();
                                    if (errors.length) {
                                        JanuaWeb.Application.errorBox(errors.join('\n'));
                                    } else {
                                        JanuaWeb.Application.toastMe('Contact and groups have been imported');
                                    }
                                }
                            }
                        });
                    } else {
                        form.unmask();
                        view.close();
                        msg = "Failed to reload group<br/>" + errors.join('\n')
                        JanuaWeb.Application.errorBox(msg);
                    }
                }
            });
        },

        importCSVFile: function(me, content) {
            var form = me.getView().getEl();
            var status = me.lookupReference('sbState');
            var groupStore = Ext.data.StoreManager.lookup('Group');
            var contactStore = Ext.data.StoreManager.lookup('Contact');
            var contactGroupStore = Ext.data.StoreManager.lookup('ContactGroup');
            var currentgroups = [];
            var importedgroups = [];
            var currentcontacts = [];
            var importedcontacts = [];
            var associatedGroups = new Ext.util.HashMap();
            var importedcontactgroup = new Ext.util.HashMap();
            var errors = [];

            groupStore.each(function(rec) {
                name = rec.get('name');
                currentgroups.push(name);
                associatedGroups.add(name, []);
            });
            contactGroupStore.each(function(rec) {
                group = groupStore.findRecord('id', rec.get('group_id'), false, false, true);
                contact = contactStore.findRecord('id', rec.get('contact_id'), false, false, true);
                associatedGroups.get(group.get('name')).push(contact.get('phone_number'));
            });
            contactStore.each(function(rec) {
                currentcontacts.push(rec.get('phone_number'));
            });
            lines = content.split(/\r?\n/);
            for (i = 0; i < lines.length; i++) {
                if (i == 0 || lines[i] == "") {
                    continue;
                }
                row = lines[i].split(',');
                firstname = row[0].replace(/["']/g,'');
                name = row[1].replace(/["']/g,'');
                phone = row[2].replace(/["']/g,'');
                email = row[3].replace(/["']/g,'');
                description = row[4].replace(/["']/g,'');
                if (row.length > 4) {
                    groups = row[5].replace(/["']/g,'').split(':');
                } else {
                    groups = [];
                }
                for (g = 0; g < groups.length; g++) {
                    group = groups[g];
                    if (group != "") {
                        if (Ext.Array.contains(currentgroups, group) == false) {
                            Ext.Array.include(importedgroups, group);
                            associatedGroups.add(group, []);
                        }
    
                        if (Ext.Array.contains(associatedGroups.get(group), phone) == false) {
                            if (!importedcontactgroup.containsKey(group)) {
                                importedcontactgroup.add(group, []);
                            }
                            Ext.Array.include(importedcontactgroup.get(group), phone);
                        }
                    }
                }
                if (Ext.Array.contains(currentcontacts, phone) == false) {
                    contact = new JanuaWeb.model.Contact({
                        'firstname': firstname,
                        'name': name,
                        'phone_number': phone,
                        'email': email,
                        'description': description
                    });
                    Ext.Array.include(importedcontacts, contact);
                }
            }

            countgroup = importedgroups.length;
            countcontact = importedcontacts.length;
            countcontactgroup = 0;
            importedcontactgroup.each(function(key, value, length) {
                countcontactgroup += value.length;
            });

            count = countgroup + countcontact;

            params = {
                'form': form,
                'contactGroupStore': contactGroupStore,
                'groupStore': groupStore,
                'contactStore': contactStore,
                'status': status,
                'countcontactgroup': countcontactgroup,
                'importedcontactgroup': importedcontactgroup,
                'scope': me,
                'view': me.getView(),
                'errors': errors
            }
            if (countgroup || countcontact) {
                status.showBusy('Importing data...');
                form.mask();
            } else {
                if (countcontactgroup) {
                    me.saveContactGroup(params);
                } else {
                    if (lines.length == 1)
                        text = 'No data to import';
                    else
                        text = 'Already up to date !';
                    status.setStatus({
                        text: text,
                        clear: true
                    });
                }    
            }
            for (i = 1; i <= countgroup; i++) {
                group = new JanuaWeb.model.Group({
                    'name': importedgroups[i-1]
                });
                group.save({
                    success: function(rec, operation) {
                        count -= 1;
                        if (count == 0) {
                            me.reloadAll(params);
                        }
                    },
                    failure: function(rec, operation) {
                        errors.push('Failed to add group ' + rec.get('name'));
                        count -= 1;
                        if (count == 0) {
                            form.unmask();
                            me.getView().close();
                            JanuaWeb.Application.errorBox(errors.join('\n'));
                        }
                    }
                });
            }

            for (i = 1; i <= countcontact; i++) {
                contact = importedcontacts[i-1];
                contact.save({
                    success: function(rec, operation) {
                        count -= 1;
                        if (count == 0) {
                            me.reloadAll(params);
                        }
                    },
                    failure: function(rec, operation) {
                        errors.push('Failed to add contact ' + rec.get('name') + ' ' + rec.get('firstname'));
                        count -= 1;
                        if (count == 0) {
                            form.unmask();
                            me.getView().close();
                            JanuaWeb.Application.errorBox(errors.join('\n'));
                        }
                    }
                });
            }
        }
    }
});
