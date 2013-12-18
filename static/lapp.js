/*global Backbone, $, _ */
var BBL = {};

/******************************************************************************/
/* LampApp model
 *
 */
var LappModel = Backbone.Model.extend({
    /* "local" attributes are:
        - selected
        - state
    */
    urlRoot: '/v1/lapps',

    log: function(msg) {
        console.log('<LAPP:' + this.id + '> ' + msg);
    },

    initialize: function() {
        this.changeState('partial'); //TODO: manage it by a default attr
        this.on('change', this.onChange);
        // attributes that are monitor to change lapp state
        this.saved_attrs = ['py_code'];
    },

    select: function() {
        this.collection.select(this);
    },

    /* update the model state
    */
    changeState: function(new_state) {
        if (_.indexOf(['partial', 'uptodate', 'modified'], new_state) >= 0) {
            this.set({'state': new_state});
            this.log('state='+ this.state);
        } else {
            throw new Error('Invalide State : ' + new_state);
        }
    },

    //override save fct to manage state
    save: function(attrs, options) {
        var result = Backbone.Model.prototype.save.call(this, attrs, options);
        var self = this;
        result.done(function() {
            self.changeState('uptodate');
        });
        return result;
    },

    //override fetch fct to manage state
    fetch: function(attrs, options) {
        var result = Backbone.Model.prototype.fetch.call(this, attrs, options);
        var self = this;
        result.done(function() {
            self.changeState('uptodate');
        });
        return result;
    },

    /* called when the model is changed, update the state
    */
    onChange: function() {
        if (this.get('state') != 'partial' && this.hasChanged(this.saved_attrs)) {
            this.changeState('modified');
        }
    }
});

/* The collection of
*/
var LappCollection = Backbone.Collection.extend({
    model: LappModel,
    url: '/v1/lapps',

    initialize: function() {
        this.selected = null;
    },

    select: function(model) {
        if (this.selected) {
            this.selected.set({selected: false});
        }
        model.set({selected: true});
        this.selected = model;
    },

   // The Twitter Search API returns tweets under "results".
    parse: function(response) {
        return response.lapps;
    }
});

/******************************************************************************/
Views = {};

/******************************************************************************/
/* current lapp view
*/
Views.LappView = Backbone.View.extend({
    template: _.template(
        '<h2><%= name %></h2> \
        <div class=\"editor\"></div> \
        <button type="button" name="save">Save</button>\
        <% if(state == \"modified\") {%>changed !<%}%>'
    ),

    events: {
        //"change textarea.py_code": "code_change", //
    },

    log: function(msg) {
        console.log('<LAPP_VIEW:'+ this.model.id + '> '+ msg);
    },

    initialize: function() {
        _(this).bindAll('render');
        this.listenTo(this.model, 'change', this.modelChanged);
    },

    modelChanged: function(model, value, option) {
        if (!_.has(value, 'from') || value.from != this) {
            this.render();
        }
    },

    render: function() {
        var self = this; // for callback functions
        this.log('render');
        this.$el.empty();
        if (this.model.get('state') == 'partial') {
            this.$el.html('Waiting for lapp data !');
        } else {
            var data = this.model.attributes;
            data['state'] = this.model.get('state');
            this.$el.html(this.template(data));
            // save button
            this.$el.find("button[name=save]").click(function(){
                self.model.save();
            });
            // create the python editor
            this.editor = ace.edit($('div.editor', this.$el)[0]);
            this.editor.setTheme('ace/theme/monokai');
            this.editor.getSession().setMode('ace/mode/python');
            this.editor.setValue(this.model.get('py_code'));
            // bind it
            this.editor.getSession().on('change', function() {
                var new_code = self.editor.getValue();
                self.log('change for' + self.model.id);
                self.model.set({'py_code': new_code}, {'from': self});
            });
        }
        return this;
    },

    remove: function() {
        this.undelegateEvents();
        this.$el.empty();
        this.stopListening();
        return this;
    }
});

/******************************************************************************/
/* Basic lapp list view
*/
Views.LappListElmt = Backbone.View.extend({

    //note: the real href is indicated however it is catched by JS
    template: _.template('<a href=\"<%= name %>\" \
        class=\"<% if (selected) { %>selected<% } %>\"\ > \
        <%= name %>\
        <% if (state==\"modified\") { %>(M)<% } %>\
        </a>'
    ),

    initialize: function() {
        _(this).bindAll('render');
        this.model.on('change', this.render);
    },

    events: {
        'click a' : 'click'
    },

    log: function(msg) {
        console.log('<LAPP_LIST_ELMT_VIEW:'+ this.model.id + '> '+ msg);
    },

    render: function() {
        this.log('render');
        var data = this.model.attributes;
        // is the
        data.selected = (BBL.current_lapp != null)
                            && (BBL.current_lapp.id == this.model.id);
        this.$el.html(this.template(data));
        return this;
    },

    click: function(event) {
        event.preventDefault(); //do not go to the indicated url in the link
        this.log(' click on a lappname');
        //this.model.set({selected: true});
        BBL.router.navigate(this.model.get('name'), {trigger: true});
    }
});

/******************************************************************************/
/* List of basic lapp view
*/
Views.LappList = Backbone.View.extend({
    append: function(model) {
        var li = $('<li>').appendTo(this.listel);
        var view = new Views.LappListElmt({
            model: model,
            el: li[0]
        });
        view.render();
    },

    initialize: function() {
        this.render();
        _(this).bindAll('append', 'render');
        this.collection.bind('refresh', this.render);
        this.collection.bind('add', this.append);
    },

    render: function() {
        $(this.el).empty();
        this.listel = $('<ul>').addClass('lapps-list').appendTo(this.el);
        this.collection.each(function(model) {
            this.append(model);
        }, this);
        return this;
    }
});

/******************************************************************************/
/* Router, to select a lapp
*/
var LampAppRouter = Backbone.Router.extend({
    routes: {
        '': 'index',
        ':lapp_name': 'open_lapp'
    },

    log: function(msg) {
        console.log('[router] ' + msg);
    },

    initialize: function() {
        this.log('<router init>');
    },

    index: function() {
        // index page setup
    },

    /* Open a lapp */
    open_lapp: function(lapp_name) {
        // lapp edit page setup
        this.log('goto ' + lapp_name);

        // destroy the old view if needed
        if (BBL.current_lapp_view) {
            this.log('remove LAPP_VIEW');
            BBL.current_lapp_view.unbind();
            BBL.current_lapp_view.remove();
        }

        // get the new model
        BBL.current_lapp = BBL.lapp_collection.get(lapp_name);
        BBL.current_lapp.select();
        if (BBL.current_lapp.get('state') == 'partial') {
            BBL.current_lapp.fetch();
        }

        // setup the view
        BBL.current_lapp_view = new Views.LappView({
            model: BBL.current_lapp,
            el: '#lapp'
        }).render();
    }
});


/******************************************************************************/
/******************************************************************************/
// setup models

BBL.init = function() {
    // common setup
    // Models
    BBL.lapp_collection = new LappCollection();
    BBL.current_lapp = null;

    // current lapp view
    BBL.current_lapp_view = null;

    // setup list view
    BBL.lapp_list = new Views.LappList({
        collection: BBL.lapp_collection,
        el: $('#lapps-list')
    });

    // setup add view
    $('#add').click(function() {
        var model = new LappModel({
            name: $('#new-name').val(),
            id: $('#new-name').val()
        });
        BBL.lapp_collection.add(model);
        model.save();
    });

    // download data and setup router
    var fetchingLapps = BBL.lapp_collection.fetch();
    fetchingLapps.done(function() {
        BBL.router = new LampAppRouter();
        // start history
        Backbone.history.start({pushState: true});
    });
};

$(function() {
    BBL.init();
});

