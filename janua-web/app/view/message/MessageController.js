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
Ext.define('JanuaWeb.view.message.MessageController', {
    extend: 'Ext.app.ViewController',

    requires: [
        'Ext.window.MessageBox'
    ],
    
    alias: 'controller.message',

    config: {
        listen : {
            controller : {
                'contactgroup' : {
                    updateContact: 'onUpdateContact',
                    updateGroup: 'onUpdateGroup'
                }
            }
        }
    },
	
	onUpdateCounter: function() {
		var smsMessage = this.lookupReference('smsMessage')
		var maxLength = smsMessage.maxLength;
		var smsBody = smsMessage.getValue();
		var smsLength = smsBody.length;

		if(smsLength >= maxLength)
			smsMessage.setRawValue(smsBody.slice(0, smsLength-(smsLength-maxLength)));

		/* textCounter has a setValue but its too damn slow, so misc hack */
		newtext = 'Your message (characters remaining: ' + (maxLength - smsLength) + ')';
		smsMessage.labelEl.dom.innerHTML = smsMessage.labelEl.dom.innerHTML.replace(this.smsCharRemainingText, newtext);
		this.smsCharRemainingText = newtext;
	},
	
	onComboDestroy: function (combo) {
		combo.getPicker().el.un(combo.mouseLeaveMonitor);
	},

	onComboExpand: function (combo) {
		combo.mouseLeaveMonitor = combo.getPicker().el.monitorMouseLeave(100, combo.collapse, combo);
	},

    onUpdateContact: function() {
        var contactbox = this.lookupReference('smsContact');       
        var form = this.lookupReference('smsForm');
        
        if (contactbox) {
			contactbox.store.reload();
			form.reset();
		}
    },
    
    onUpdateGroup: function() {
        var groupbox = this.lookupReference('smsGroup');
        var form = this.lookupReference('smsForm');
        
        if (groupbox) {
			groupbox.store.reload();
			form.reset();
		}
    },

    onSendMessage: function(source) {
        var me = this;
        var form = this.lookupReference('smsForm');
        var fn = Ext.Function.bind(this.onSendConfirm, this, form, true);
        JanuaWeb.Application.confirmBox('Send this message ?', fn, this);
    },
    
    onSendConfirm: function(button, text, eventOptions, form) {
        var me = this;
        var values = form.getValues();
        var data = {
            message: '',
            to: ''
        }
		var mail = {
			subject: '',
			message: '',
			to: ''
		}
		var conn = new Ext.data.Connection();

        if (button == 'yes') {
            if (values['message'] == '') {
                JanuaWeb.Application.errorBox('You try to submit an empty message');
                return;
            }
			if ('sendmail' in values) {
				if (values['mail_subject'].length == 0 || values['mail_message'].length == 0) {
					JanuaWeb.Application.errorBox('There is no mail subject and/or message');
					return;
				}
			}
            data.message = values['message'];

            if ('sendall' in values) {
                data.to = 'all';
            } else {
                if (values['groups'].length > 0) {
                    data.to += values['groups'].join(',')
                }
                if (values['contacts'].length > 0) {
                    data.to += ',' + values['contacts'].join(',')
                }
				if (values['groups'].length == 0 && values['contacts'].length == 0) {
					JanuaWeb.Application.errorBox('You don\'t have set recipients');
					return;
				}
            }
            conn.request({
                url: '/sendsms',
                method: 'POST',
                params: Ext.JSON.encode(data),
                scope: me,
                callback: me.onSendReturn,
                original: form.getValues(),
				headers: {
					'JanuaAuthToken': Ext.util.Cookies.get("auth_token"),
					'Content-Type': 'application/json'
				}
            });
			if ('sendmail' in values) {
				mail.to = data.to;
				mail.subject = values['mail_subject'];
				mail.message = values['mail_message'];
				conn.request({
					url: '/sendmail',
					method: 'POST',
					params: Ext.JSON.encode(mail),
					scope: me,
					callback: me.onSendReturn,
					original: form.getValues(),
					headers: {
						'JanuaAuthToken': Ext.util.Cookies.get("auth_token"),
						'Content-Type': 'application/json'
					}
				});
			}
            form.reset();
        }
    },

    onSendReturn: function(options, success, response) {
        var me = this;
        if (success) {
            var resp = Ext.decode(response.responseText);
            if (resp.success) {
                JanuaWeb.Application.toastMe(resp.message);
            } else {
                JanuaWeb.Application.errorBox(resp.message);
            }
        } else {
            if (response.statusText)
                JanuaWeb.Application.errorBox('Server return status: ' + response.statusText);
            else
                JanuaWeb.Application.errorBox('Server not responding');
        }
		this.onUpdateCounter();
    },

    privates: {
        smsCharRemainingText: 'Characters remaining: 480'
    }
});
