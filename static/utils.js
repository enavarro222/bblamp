/**
 * Use Backbone Events listenTo/stopListening with any DOM element
 *
 * @param {DOM Element}
 * @return {Backbone Events style object}
 **/
function asEvents(el) {
    var args;
    return {
        on: function(event, handler) {
            if (args) throw new Error("this is one off wrapper");
            el.addEventListener(event, handler, false);
            args = [event, handler];
        },
        off: function() {
            el.removeEventListener.apply(el, args);
        }

    };
}

/**
 * Use Backbone Events listenTo/stopListening with Mousetrap
 *
 * @return {Backbone Events style object}
 **/
function bbMousetrap(global) {
    var args;
    return {
        on: function(keys, handler) {
            if (args) throw new Error("this is one off wrapper");
            if(global){
                Mousetrap.bindGlobal(keys, handler);
            } else {
                Mousetrap.bind(keys, handler);
            }
            args = keys;
        },
        off: function() {
            Mousetrap.unbind(args);
        }

    };
}

/* i18n view */
var i18nLayout = Backbone.Layout.extend({
    afterRender: function() {
        $(this.el).i18n();
        if(this._afterRender){
            this._afterRender();
        }
    },
});

/* Colors */
function rgbToHex(R,G,B) {return toHex(R)+toHex(G)+toHex(B)}
function toHex(n) {
 n = parseInt(n,10);
 if (isNaN(n)) return "00";
 n = Math.max(0,Math.min(n,255));
 return "0123456789ABCDEF".charAt((n-n%16)/16)
      + "0123456789ABCDEF".charAt(n%16);
}
