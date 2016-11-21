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
Ext.define('JanuaWeb.view.group.ContactGroupController', {
    extend: 'Ext.app.ViewController',

    requires: [
        'Ext.window.MessageBox',
        'JanuaWeb.view.group.AddContactWindow',
        'JanuaWeb.view.group.EditContactWindow',
        'JanuaWeb.view.group.AddGroupWindow',
        'JanuaWeb.view.group.EditGroupWindow'
    ],
    
    alias: 'controller.contactgroup',
	
	onSearchGroup: function(me, newValue, oldValue, eOpts) {
		var groupStore = Ext.data.StoreManager.lookup("Group");
		groupStore.clearFilter();
		if (newValue != '') {
			groupStore.filter([{property: "name", value: newValue}]);
		}
	},
	
	onSearchContact: function(me, newValue, oldValue, eOpts) {
		var contactStore = Ext.data.StoreManager.lookup("Contact");
		contactStore.clearFilter();
		if (newValue != '') {
			contactStore.filter([{property: "name", value: newValue}])
		}
	},
	
    onAddContactClick: function(source) {
    	var widget = Ext.widget('AddContactWindow');
		var contactView = widget.getViewModel();
		var contact = new JanuaWeb.model.Contact();
	
		contactView.setData({contact: contact});
    },

    onEditContactClick: function(source) {
		var record = source.getWidgetRecord();
		var widget = Ext.widget('EditContactWindow');
		var contactView = widget.getViewModel();

		contactView.setData({contact: record});
    },

    onDeleteContactClick: function(source) {
		var me = this;
		var record = source.getWidgetRecord();
		var fn = Ext.Function.bind(this.onDeleteContactConfirm, this, record, true);
		JanuaWeb.Application.confirmBox('Delete ' + record.get('firstname') + ' ' + record.get('name'), fn, this);
	},

	onDeleteContactConfirm: function(button, text, eventOptions, record) {
		var me = this;
		if (button == 'yes') {
			record.erase({
				success: function(rec, operation) {
					var groupStore = Ext.data.StoreManager.lookup("Group");
					var contactGroups = Ext.data.StoreManager.lookup("ContactGroup");
					var contactStore = Ext.data.StoreManager.lookup("Contact");

					JanuaWeb.Application.toastMe('Contact ' + rec.get('firstname') + ' ' + rec.get('name') + ' has been deleted');
					groupStore.reload();
					contactGroups.reload();
					contactStore.reload();
					me.fireEvent('updateContact');
					me.fireEvent('updateAction');
				},
				failure: function(rec, operation) {
					JanuaWeb.Application.errorBox('Failed to delete contact ' + rec.get('firstname') + ' ' + rec.get('name'), operation);
				}
			});
		}
	},
	
    onAddGroupClick: function(source) {
    	var widget = Ext.widget('AddGroupWindow');
		var groupView = widget.getViewModel();
		var group = new JanuaWeb.model.Group();
	
		groupView.setData({group: group});
    },
    
    onEditGroupClick: function(source) {
		var record = source.getWidgetRecord();
		var widget = Ext.widget('EditGroupWindow');
		var contactView = widget.getViewModel();

		contactView.setData({group: record});
    },

    onDeleteGroupClick: function(source) {
		var me = this;
		var record = source.getWidgetRecord();
		var fn = Ext.Function.bind(this.onDeleteGroupConfirm, this, record, true);
		JanuaWeb.Application.confirmBox('Delete ' + record.get('name'), fn, this);
	},

	onDeleteGroupConfirm: function(button, text, eventOptions, record) {
		var me = this;
		if (button == 'yes') {
			record.erase({
				success: function(rec, operation) {
					var contactStore = Ext.data.StoreManager.lookup("Contact");
					var contactGroups = Ext.data.StoreManager.lookup("ContactGroup");
					var groupStore = Ext.data.StoreManager.lookup("Group");
					JanuaWeb.Application.toastMe('Group ' + rec.get('name') + ' has been deleted');
					contactStore.reload();
					contactGroups.reload();
					groupStore.reload();
					me.fireEvent('updateGroup');
					me.fireEvent('updateAction');
				},
				failure: function(rec, operation) {
					JanuaWeb.Application.errorBox('Failed to delete group ' + rec.get('name'), operation);
				}
			});
		}
	},
	
	onCloseContactWindow: function() {
		var view = this.getView();
		var contact = view.getViewModel().getData().contact;

		contact.reject();
		contact.groups().rejectChanges();

		this.closeWindow(view);
	},

	onSaveContactWindow: function() {
		var me = this;
		var view = this.getView();
		var contact = view.getViewModel().getData().contact;
		var groups = Ext.data.StoreManager.lookup("Group");
		var firstname = this.lookupReference('editContactFirstname');
		var name = this.lookupReference('editContactName');
		var phone = this.lookupReference('editContactPhone');
		var email = this.lookupReference('editContactMail');

		if (firstname.wasValid == false || name.wasValid == false || phone.wasValid == false || email.wasValid == false) {
			var invalidFields = [];
			if (firstname.wasValid == false)
				invalidFields.push('firstname');
			if (name.wasValid == false)
				invalidFields.push('name');
			if (phone.wasValid == false)
				invalidFields.push('phone number');
			if (email.wasValid == false)
				invalidFields.push('email');

			contact.reject();
			JanuaWeb.Application.errorBox('There is invalid fields : ' + invalidFields.join(', '));
		} else {
			if (Ext.Object.getSize(contact.getChanges())) {
				contact.save({
					success: function(rec, operation) {
						JanuaWeb.Application.toastMe('Contact ' + rec.get('firstname') + ' ' + rec.get('name') + ' has been updated');
						groups.reload();
						me.fireEvent('updateContact');
						me.fireEvent('updateAction');
					},
					failure: function(rec, operation) {
						JanuaWeb.Application.errorBox('Failed to edit contact ' + rec.get('firstname') + ' ' + rec.get('name'), operation);
						contact.reject();
					}
				});
			}
		}
		JanuaWeb.Application.saveUs(this.contactConfig, contact.groups(), contact.id);

		this.closeWindow(view);
	},

	onCreateContactWindow: function(source) {
		var me = this;
		var view = this.getViewModel().getView();
		var contacts = Ext.data.StoreManager.lookup("Contact");
		var contact = this.getViewModel().getData().contact;

		if (Ext.Object.getSize(contact.getChanges())) {
			contact.save({
				success: function(rec, operation) {
					JanuaWeb.Application.toastMe('Contact ' + rec.get('firstname') + ' ' + rec.get('name') + ' has been created');
					contacts.reload();
					me.fireEvent('updateContact');
				},
				failure: function(rec, operation) {
					JanuaWeb.Application.errorBox('Failed to create contact ' + rec.get('firstname') + ' ' + rec.get('name'), operation);
				}
			});
		}
		this.closeWindow(view);
	},
	
	onCloseGroupWindow: function() {
		var view = this.getView();
		var group = view.getViewModel().getData().group;
		var contactGroupStore = Ext.data.StoreManager.lookup("ContactGroup");

		group.reject();
		group.contacts().rejectChanges();
		this.closeWindow(view);
	},

	onSaveGroupWindow: function() {
		var me = this;
		var view = this.getView();
		var group = view.getViewModel().getData().group;
		var contacts = Ext.data.StoreManager.lookup("Contact");
		var name = this.lookupReference('editGroupName');

		if (name.wasValid == false) {
			group.reject();
			me.errorBox('Group name is invalid');
		} else {
			if (Ext.Object.getSize(group.getChanges())) {
				group.save({
					success: function(rec, operation) {
						JanuaWeb.Application.toastMe('Group ' + rec.get('name') + ' has been updated');
						contacts.reload();
						me.fireEvent('updateGroup');
						me.fireEvent('updateAction');
					},
					failure: function(rec, operation) {
						JanuaWeb.Application.errorBox('Failed to edit group ' + rec.get('name'), operation);
						group.reject();
					}
				});
			}
		}
		JanuaWeb.Application.saveUs(this.groupConfig, group.contacts(), group.id);

		this.closeWindow(view);
	},

	onCreateGroupWindow: function() {
		var me = this;
		var view = this.getViewModel().getView();
		var groups = Ext.data.StoreManager.lookup("Group");
		var group = this.getViewModel().getData().group;

		if (Ext.Object.getSize(group.getChanges())) {
			group.save({
				success: function(rec, operation) {
					JanuaWeb.Application.toastMe('Group ' + rec.get('name') + ' has been created');
					groups.reload();
					me.fireEvent('updateGroup');
				},
				failure: function(rec, operation) {
					JanuaWeb.Application.errorBox('Failed to create group ' + rec.get('name'), operation);
				}
			});
		}
		this.closeWindow(view);
	},

	submitOnEnter: function(field, el) {
		if (el.getKey() == Ext.EventObject.ENTER) {
			var button = field.up().lookupReference('submitButton');
			if (button.disabled == false)
				button.fireEvent('click');
		}
	},
				
	privates: {
		closeWindow: function(view) {
			var action;

			if (view) {
				action = this.getCloseViewAction();
				view[action]();
			}
		},
		groupConfig: {
			manyStore: 'ContactGroup',
			manyModel: 'JanuaWeb.model.ContactGroup',
			primaryKey: 'group_id',
			secondaryKey: 'contact_id',
			successMessage: "Group contacts has been updated",
			failureMessage: "Failed to update group contacts",
			reloadStores: ["Contact", "Action"]
		},
		contactConfig: {
			manyStore: 'ContactGroup',
			manyModel: 'JanuaWeb.model.ContactGroup',
			primaryKey: 'contact_id',
			secondaryKey: 'group_id',
			successMessage: "Contact groups has been updated",
			failureMessage: "Failed to update contact groups",
			reloadStores: ["Group", "Action"]
		}
	}
});
