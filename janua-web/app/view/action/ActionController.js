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
Ext.define('JanuaWeb.view.action.ActionController', {
    extend: 'Ext.app.ViewController',

    requires: [
        'Ext.window.MessageBox',
        'JanuaWeb.view.action.AuthorizedGroupWindow',
        'JanuaWeb.view.action.AuthorizedSupervisorWindow',
        'JanuaWeb.view.action.ManagedByWindow',
        'JanuaWeb.view.action.ContactNotifyGrid'
    ],

    alias: 'controller.action',
    config: {
        listen : {
            controller : {
                '*' : {
                    updateAction: 'onUpdateAction'
                }
            }
        }
    },

    onUpdateAction: function() {
        var grid = this.lookupReference('actionGrid');
        if (grid) {
            grid.getStore().reload();
        }
    },

    onActionRefresh: function() {
        var actionStore = Ext.data.StoreManager.lookup("Action");
        actionStore.reload();
    },

    onAuthorizedGroupClick: function(source) {
        var record = source.getWidgetRecord();
        var widget = Ext.widget('AuthorizedGroupWindow');
        var view = widget.getViewModel();

        view.setData({action: record});
    },

    onAuthorizedSupervisorClick: function(source) {
        var record = source.getWidgetRecord();
        var widget = Ext.widget('AuthorizedSupervisorWindow');
        var view = widget.getViewModel();

        view.setData({action: record});
    },

    onContactNotifyClick: function(source) {
        var record = source.getWidgetRecord();
        var widget = Ext.widget('ContactNotifyGrid');
        var view = widget.getViewModel();
        var authorizedGroupStore = Ext.data.StoreManager.lookup("AuthorizedGroupAction");
        var contactGroupStore = Ext.data.StoreManager.lookup("ContactGroup");
        var contactStore = Ext.data.StoreManager.lookup("Contact");
        var groupStore = Ext.data.StoreManager.lookup("Group");
        var contactNotifyActionStore = Ext.data.StoreManager.lookup("ContactNotifyAction");
        var contactNotifyGroupStore = Ext.data.StoreManager.lookup("ContactNotifyGroup");
        var index = 1;

        authorizedGroupStore.each(function(rec) {
            if (rec.get('action_id') == record.id) {
                var group_id = rec.get('group_id');
                group = groupStore.findRecord('id', group_id, 0, false, false, true);
                contactGroupStore.filter([
                    {property: 'group_id', value: group_id}
                ]);
                contactGroupStore.each(function(rec) {
                    contact = contactStore.findRecord('id', rec.get('contact_id'), 0, false, false, true);
                    model = new JanuaWeb.model.ContactNotifyGroup({
                        id: index,
                        group: group.get('name'),
                        group_id: group_id,
                        contact: contact.get('fullname'),
                        contact_id: contact.id,
                        action_id: record.id
                    });
                    contactNotifyGroupStore.add(model);
                    contactNotifyActionStore.filter([
                        {property: 'action_id', value: record.id},
                        {property: 'contact_id', value: contact.id},
                        {property: 'group_id', value: group_id}
                    ]);
                    if (contactNotifyActionStore.getData().length > 0) {
                        widget.getView().getSelectionModel().select(model, true);
                    }
                    contactNotifyActionStore.clearFilter();
                    index++;
                });
                groupStore.clearFilter();
            }
        });
        widget.setTitle('Contact group to notify for ' + record.get('name'));
        view.setData({action: record});
    },
    
    onCloseAuthorizedGroupWindow: function() {
        var view = this.getView();
        var action = view.getViewModel().getData().action;

        action.authorized_group().rejectChanges();

        this.closeView(view);
    },

    onCloseAuthorizedSupervisorWindow: function() {
        var view = this.getView();
        var action = view.getViewModel().getData().action;

        action.authorized_supervisor().rejectChanges();
        this.closeView(view);
    },

    onCloseContactNotifyWindow: function() {
        var view = this.getView();
        var action = view.getViewModel().getData().action;

        view.getStore().removeAll();

        this.closeView(view);
    },

    onSaveAuthorizedGroupWindow: function() {
        var view = this.getView();
        var action = view.getViewModel().getData().action;

        JanuaWeb.Application.saveUs(this.authorizedGroupConfig, action.authorized_group(), action.id);
        
        this.closeView(view);
    },

    onSaveAuthorizedSupervisorWindow: function() {
        var view = this.getView();
        var action = view.getViewModel().getData().action;

        JanuaWeb.Application.saveUs(this.authorizedSupervisorConfig, action.authorized_supervisor(), action.id);
        
        this.closeView(view);
    },

    onSaveContactNotifyWindow: function() {
        var view = this.getView();
        var action = view.getViewModel().getData().action;
        var contactNotifyActionStore = Ext.data.StoreManager.lookup("ContactNotifyAction");
        var contactNotifyGroupStore = view.getStore();
        var removed = [];
        var added = [];

        contactNotifyActionStore.each(function(rec) {
            if (rec.get('action_id') == action.id) {
                found = false;
                Ext.Array.each(view.getSelectionModel().getSelection(), function(select) {
                    if (select.get('group_id') == rec.get('group_id') && select.get('contact_id') == rec.get('contact_id') && select.get('action_id') == rec.get('action_id')) {
                        found = true;
                    }
                });
                if (!found) {
                    removed.push(rec);
                }
            }
        });
        Ext.Array.each(removed, function(rec) {
            contactNotifyActionStore.remove(rec);
        });
        Ext.Array.each(view.getSelectionModel().getSelection(), function(select) {
            found = false;
            contactNotifyActionStore.each(function(rec) {
                if (select.get('group_id') == rec.get('group_id') && select.get('contact_id') == rec.get('contact_id') && select.get('action_id') == rec.get('action_id')) {
                    found = true;
                }
            });
            if (!found) {
                model = new JanuaWeb.model.ContactNotifyAction({
                    group_id: select.get('group_id'),
                    action_id: select.get('action_id'),
                    contact_id: select.get('contact_id')
                });
                added.push(model);
            }
        });
        Ext.Array.each(added, function(rec) {
            contactNotifyActionStore.add(rec);
        });
        contactNotifyActionStore.sync({
            success: function() {
                JanuaWeb.Application.toastMe('Contact group notify for action ' + action.get('name') + ' has been updated');
                contactNotifyActionStore.reload();
            },
            failure: function() {
                JanuaWeb.Application.errorBox('Failed to modify contact group notify');
                contactNotifyActionStore.reload();
            }
        });
        contactNotifyGroupStore.removeAll();
        this.closeView(view);
    },

    onManagedByClick: function(source) {
        var record = source.getWidgetRecord();
        var widget = Ext.widget('ManagedByWindow');
        var view = widget.getViewModel();

        view.setData({action: record});
    },

    onSaveManagedByWindow: function() {
        var view = this.getView();
        var action = view.getViewModel().getData().action;
        var adminStore = view.getViewModel().getStore('Admins');
        var comboValue = view.lookupReference('comboAdmin').getValue();
        var admin = adminStore.findRecord('display', comboValue);
        var reloadStore = ['Action', 'AuthorizedGroupAction', 'ContactNotifyAction', 'AuthorizedSupervisorAction'];
        
        if (admin.id != action.get('admin_id')) {
            action.set('admin_id', admin.id);
            action.save({
                success: function(rec, operation) {
                    JanuaWeb.Application.toastMe('Action ' + rec.get('name') + ' manager has been updated');
                    Ext.each(reloadStore, function(store) {
                        Ext.data.StoreManager.lookup(store).reload();
                    });
                },
                failure: function(rec, operation) {
                    JanuaWeb.Application.errorBox('Failed to change manager', operation);
                }
            });
        }

        this.closeView(view);
    },

    privates: {
        closeWindow: function(view) {
            var action;

            if (view) {
                action = this.getCloseViewAction();
                view[action]();
            }
        },
        authorizedGroupConfig: {
            manyStore: 'AuthorizedGroupAction',
            manyModel: 'JanuaWeb.model.AuthorizedGroupAction',
            primaryKey: 'action_id',
            secondaryKey: 'group_id',
            successMessage: "Authorized group has been updated",
            failureMessage: "Failed to update authorized group",
            reloadStores: ['Action','ContactNotifyAction']
        },
        authorizedSupervisorConfig: {
            manyStore: 'AuthorizedSupervisorAction',
            manyModel: 'JanuaWeb.model.AuthorizedSupervisorAction',
            primaryKey: 'action_id',
            secondaryKey: 'admin_id',
            successMessage: "Authorized supervisor has been updated",
            failureMessage: "Failed to update authorized supervisor"
        }
    }
});
