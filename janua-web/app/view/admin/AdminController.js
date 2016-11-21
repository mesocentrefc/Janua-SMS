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
Ext.define('JanuaWeb.view.admin.AdminController', {
    extend: 'Ext.app.ViewController',

    requires: [
        'Ext.window.MessageBox',
        'JanuaWeb.view.admin.AddAdminWindow',
        'JanuaWeb.view.admin.EditAdminWindow'
    ],
    
    alias: 'controller.admin',

	onGeneratePasswordCreate: function(me) {
		me.generate('p1', 'p2', 8);
	},

	onGeneratePasswordEdit: function(me) {
		me.generate('adp1', 'adp2', 8);
	},

    onAddAdminClick: function(source) {
		var widget = Ext.widget('AddAdminWindow');
		var adminView = widget.getViewModel();
		var admin = new JanuaWeb.model.Admin();

		adminView.setData({admin: admin});
    },
    
    onEditAdminClick: function(source) {
    	var record = source.getWidgetRecord();
    	var widget = Ext.widget('EditAdminWindow');
		var adminView = widget.getViewModel();

		adminView.setData({admin: record});
    },
	
	onCreateAdminWindow: function() {
		var me = this;
		var view = this.getView();
		var admin = this.getViewModel().getData().admin;
		var adminStore = Ext.data.StoreManager.lookup("Admin");
		var passgen = me.lookupReference('generatePassword');
		passgen.generate('p1', 'p2', 8);

		if (Ext.Object.getSize(admin.getChanges())) {
			admin.save({
				success: function(rec, operation) {
					JanuaWeb.Application.infoBox(
						'Admin ' + rec.get('firstname') + ' ' + rec.get('name') + ' has been created',
						rec.get('firstname') + ' ' + rec.get('name') + ' credentials:<br/>' +
						'<b>Username:</b> ' + rec.get('phone_number') + '<br/>' +
						'<b>Password:</b> ' + passgen.password);
					adminStore.reload();
				},
				failure: function(rec, operation) {
					JanuaWeb.Application.errorBox('Failed to create admin ' + rec.get('firstname') + ' ' + rec.get('name'), operation);
				}
			});
		}
		this.closeWindow(view);
	},
	
	onCloseAdminWindow: function() {
		var view = this.getView();

		rec = view.getViewModel().getData().admin;
		rec.reject();
		
		this.closeWindow(view);
	},

	onSaveAdminWindow: function() {
		var me = this;
		var view = this.getView();

		var pass1 = Ext.getCmp('adp1');
		var pass2 = Ext.getCmp('adp2');
		var quota_limit = Ext.getCmp('quota_limit');
		var quota_unit = Ext.getCmp('quota_unit');

		admin = view.getViewModel().getData().admin;
		admin.set('sms_quota', quota_limit.value + " " + quota_unit.value);

		if (pass1.value != '' && (pass1.value == pass2.value)) {
			admin.set('password', pass1.value);
		}
		if (pass1.value != '' && (pass1.value != pass2.value)) {
			JanuaWeb.Application.errorBox('Password confirmation doesn\'t match');
		} else {
			if (Ext.Object.getSize(admin.getChanges())) {
				admin.save({
					success: function(record, operation) {
						JanuaWeb.Application.toastMe('Changes has been applied');
						me.fireEvent('updateAction');
						record.set('quota_limit', quota_limit);
						record.set('quota_unit', quota_unit);
					},
					failure: function(record, operation) {
						admin.reject();
						JanuaWeb.Application.errorBox('', operation);
					}
				});
			}
	
			this.closeWindow(view);
		}
	},

    onDeleteAdminClick: function(source) {
		var me = this;
		var record = source.getWidgetRecord();
		Ext.Mess
		var fn = Ext.Function.bind(this.onDeleteAdminConfirm, this, record, true);
		JanuaWeb.Application.warningBox(
			'Delete ' + record.get('firstname') + ' ' + record.get('name'),
			'Delete an admin entry will also delete all entries ' +
			'associated to, including groups and contacts. ' +
			'Are you sure ?',
			fn,
			this
		);
	},

	onDeleteAdminConfirm: function(button, text, eventOptions, record) {
		var me = this;
		if (button == 'yes') {
			var adminStore = Ext.data.StoreManager.lookup("Admin");
			record.erase({
				success: function(rec, operation) {
					JanuaWeb.Application.toastMe('Admin ' + rec.get('firstname') + ' ' + rec.get('name') + ' has been deleted');
					adminStore.reload();
					Ext.data.StoreManager.lookup("Action").reload();
				},
				failure: function(rec, operation) {
					JanuaWeb.Application.errorBox('Failed to delete admin ' + rec.get('firstname') + ' ' + rec.get('name'), operation);
					adminStore.reload();
				}
			});
		}
	},

	onRefresh: function() {
		var smsStore = Ext.data.StoreManager.lookup("Sms");
		smsStore.reload();
	},
	
	onRenderAdminLevel: function(value) {
		var levelStore = Ext.data.StoreManager.lookup("AdminLevel");
		return levelStore.findRecord("value", value).get('name');
	},

	onRenderAdminQuota: function(value) {
		var squota = Ext.String.splitWords(value);
		return squota[0] + " sms per " + JanuaWeb.Application.quotaUnit[squota[1]];
	},

	onChangePassword: function(me, newValue, oldValue, eOpts) {
		var pass1 = Ext.getCmp('adp1');
		var pass2 = Ext.getCmp('adp2');

		if (newValue == false) {
			pass1.setValue('');
			pass2.setValue('');
			this.lookupReference('generatePasswordButton').setDisabled(true);
		} else {
			this.lookupReference('generatePasswordButton').setDisabled(false);
		}
	},

	privates: {
		closeWindow: function(view) {
			var action;

			if (view) {
				action = this.getCloseViewAction();
				view[action]();
			}
		}
	}
});
