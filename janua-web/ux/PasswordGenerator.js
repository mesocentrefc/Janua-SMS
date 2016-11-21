/**
 * Password generator button, useful in signup/registration forms.
 *
 * @author Roland van Wanrooy (walldorff)
 * @date   March 8, 2010
 */


Ext.namespace('Ext.ux.PasswordGenerator');

/**
 * @class Ext.ux.PasswordGenerator.Button
 * @extends Ext.Button
 *
 * A specific {@link Ext.Button} that can be used to populate 2 password fields with a
 * very strong password, which meets the highest security standards as advertises by
 * The Password Meter (http://www.passwordmeter.com/)).
 *
 * Instantiate this class anywhere in the form and apply the class method generate()
 * in the handler of the button.
 *
 * @param {Object} config The config object
 */

Ext.define('Ext.ux.PasswordGenerator', {
    extend: 'Ext.Button',

    alias: 'widget.passgen',

    /**
     * @cfg {String} text The button text. Defaults to "Generate".
     */
    text             : 'Generate'

    /**
     * @cfg {String} tooltip The tooltip of this component.
     * Defaults to "Generate password".
     */
    ,tooltip         : 'Generate password'


    ,initComponent     : function() {
        Ext.apply(this, {
            /**
             * @cfg {Array} stores The 4 stores contain the 4 different strings, from
             * which the password shall be generated. Each store contains a stock (the
             * specific string), an id for readability purpose and 2 boolean flags to
             * indicate whether the store is closed for the moment, or completely out
             * of stock (hence closed permanently).
             *
             * When a character is fetched from the store, the following actions will
             * be taken:
             * - the store will be temporarily closed to prevent consecutive characters
             *   from the same store AND to ensure that all stores are "visited";
             * - the character will be removed from the stock to prevent multiple
             *   occurrences of the same character;
             * - if the character is from the "lower" or "upper" store, then the "lower"
             *   or "upper" version of the fetched one will be further ignored, because
             *   this standard is case-insensitive;
             * - if there are no more characters left in the stock, the store will be
             *   closed permanently by assigning TRUE to the flag <em>soldOut</em>.
             */
            stores         : [{
                    id         : 'lower'
                    ,open    : true
                    // not included: "l"(lower L) to prevent mixing up with "1"(one)
                    ,stock    : 'abcdefghijkmnopqrstuvwxyz'
                    ,soldOut: false
                },{
                    id         : 'upper'
                    ,open    : true
                    // not included: "I"(upper i) and "O"(upper o) to prevent mixing
                    // up with "1"(one) and "0"(zero)
                    ,stock    : 'ABCDEFGHJKLMNPQRSTUVWXYZ'
                    ,soldOut: false
                },{
                    id         : 'number'
                    ,open    : true
                    // not included: "1"(one) and "0"(zero) to prevent mixing up
                    // with "I"(upper i)/"l"(lower L) and "O"(upper o)
                    ,stock    : '23456789'
                    ,soldOut: false
                }/*,{
                    id         : 'token'
                    ,open    : true
                    ,stock    : '/!@#$%^&*()_+[]~<>-:{}.,;:'
                    ,soldOut: false
            }*/]
        
            /**
             * @cfg {Object} store Current store, that provides the current character.
             */
            ,store             : null
        
            /**
             * @cfg {Number} stockSize The lenth of the character string in the store.
             * Short notation of <em>this.stores[n].stock.length</em>.
             */
            ,stockSize        : 0
        
            /**
             * @cfg {Number} pickPos Position of the current fetch character in the stock.
             */
            ,pickPos         : 0
        
            /**
             * @cfg {String} pickChar The fetched character.
             */
            ,pickChar         : ''
        
            /**
             * @cfg {String} password The placeholder for the newbuild password.
             */
            ,password        : ''
        });
        this.callParent(arguments);
      }


    /**
     * Called by the {@link Ext.Button} handler. 
     * Main method, which generates the password.
     *
      * @param {String} initialPassFieldID The id of the main password field
      * @param {String} confirmPassFieldID The id of the field, from which the user
     * input in the initial password field will be checked.
      * Both password fields should have the same value.
     */
    ,generate: function(initialPassFieldID, confirmPassFieldID, length) {
        var i = 0;
        // array of field components
        var fields = new Array(Ext.getCmp(initialPassFieldID), Ext.getCmp(confirmPassFieldID));
        // the length of the password. Defaults to 10.
        var passwordSize = length || initialPassFieldID.minLength || 10;

        // start with brand new stores in the original state
        this.reset();

        // generate
        while (i < passwordSize) {
            // see if all the stores are closed; if so, open them.
            this.openStores();
            // pick a store
            this.pickStore();
            // fetch a character and add it to the new password string
            this.fetchChar();
            // delete the char from the stock, so this won't be picked again
            this.deleteChar();
            // add the char to the new password string
            this.password += this.pickChar;

            i++;
        }

        // populate and validate the 2 password fields
          Ext.each(fields, function(item, index, allItems) {
             var field = fields[index];
            field.setValue(this.password);

            if (field.validate()) {
                // change background to indicate the valid state of the field
                field.addCls('x-field-valid');
            } else {
                // academical; it is very unlikely that the script reaches this point,
                // because the password will meet the highest standards.
                field.removeCls('x-field-valid');
            }
          }, this);
    }

    /**
     * Called by {@link #generate()}. Resets all stores to the
     * original state. This method is called every time the user clicks the button.
     */
    ,reset        : function() {
        this.store         = null;
        this.pickPos     = 0;
        this.pickChar     = '';
        this.stockSize    = 0;
        this.password    = '';
        var i;

        for (i = 0; i < this.stores.length; i++) {
            // short
            var s = this.stores[i];
            s.open = true;
            s.soldOut = false;
            switch(s.id) {
                case 'lower' : s.stock = 'abcdefghijkmnopqrstuvwxyz'; break;
                case 'upper' : s.stock = 'ABCDEFGHJKLMNPQRSTUVWXYZ'; break;
                case 'number': s.stock = '23456789'; break;
                //case 'token' : s.stock = '/!@#$%^&*()_+[]~<>-:{}.,;:'; break;
            }
        }
    }

    /**
     * Gets called by {@link #generate()}. Checks if all the stores
     * are closed. Reopens the stores which have a stock. Keeps the current store
     * closed in orderto prevent consecutive chars from the same store.
     */
    ,openStores    : function() {
        var i, closed = 0;
        // count the closed stores
        for (i = 0; i < this.stores.length; i++) {
            if (!this.stores[i].open) {
                closed++;
            }
        }
        // if all the stores are closed, open them all up again if they're not sold out...
        if (closed == this.stores.length) {
            Ext.each(this.stores, function(item, index, allItems) {
                    this.stores[index].open = !this.stores[index].soldOut;
            }, this);
            // ...except for the last one. 
            // Close the last store again; we don't want consecutives
            if (Ext.isObject(this.store)) {
                this.store.open = false;
            }
        }
    }

    /**
     * Called by {@link #generate()}. Determines which store will be
     * the current store. Will be limited to one of the currently open stores.
     */
    ,pickStore        : function() {
        // pick a store (index of stores)
        var index = Math.floor(Math.random()*this.stores.length);
        // see if it's open
        while ( (this.store = this.stores[ index ]).open == false ) {
            index = Math.floor(Math.random()*this.stores.length);
        }
        // short notation in class var
        this.stockSize = this.store.stock.length;
    }

    /**
     * Called by {@link #generate()}. Takes one character from the
     * current store. Picks another store and checks if the password string contains an 
     * upper/lowercase equivalent of the current character.
     * For comparison of the char against the password, both have to be formatted to 
     * upper string.
     * If the comparison is successful, then this means that the char came from the upper
     * or lower stock; therefore it is inevitable to choose another stock entirely.
     */
    ,fetchChar        : function() {
        // pick a positon from which the character is pulled out of the stock
        this.pickPos   = Math.floor(Math.random()*this.stockSize);
        // pick that character
        this.pickChar  = this.store.stock.charAt(this.pickPos);

        // compare the char against the password, in order to determine the occurrence of other-case equivalent.
        while ( (this.password.toUpperCase().lastIndexOf(this.pickChar.toUpperCase())) > -1 ) {
            // comparison succesful; pick a new store
            this.pickStore();
            // pick a positon from which the character is pulled out of the stock
            this.pickPos   = Math.floor(Math.random()*this.stockSize);
            // pick that character
            this.pickChar  = this.store.stock.charAt(this.pickPos);
        }

    }

    /**
     * Called by {@link #generate()}. Deletes the charachter from the stock and
     * checks the store for an <em>out of stock</em> status.
     * If this is the case, then this store will remain closed permanently.
     */
    ,deleteChar     : function() {
        // see if we're sold out (i.e. if the stock is empty, once this character has been removed)
        if (this.stockSize == 1) {
            this.store.soldOut = true;
        } else{
            // we're not going to be out of stock, so remove the char.
            if (this.pickPos == 0) {
                this.store.stock = this.store.stock.substr(1);
            } else if (this.pickPos == this.stockSize) {
                this.store.stock = this.store.stock.substr(0, this.stockSize-1);
            } else {
                this.store.stock = this.store.stock.substr(0, this.pickPos) + this.store.stock.substr(this.pickPos+1);
            }
        }
        // close the store for now, because next the character has to be chosen from another store
        // (or because it is out of stock)
        this.store.open = false;
    }

});  