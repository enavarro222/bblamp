/*global Backbone, $, _ */
var BBL = {};

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
        // unselect a lapp (if any)
        BBL.lapp_collection.unselect();
    },

    /* Open a lapp */
    open_lapp: function(lapp_name) {
        // lapp edit page setup
        this.log('goto ' + lapp_name);

        // get and set the new model
        var selected_lapp = BBL.lapp_collection.get(lapp_name);
        if (selected_lapp.get('state') == 'partial') {
            selected_lapp.fetch();
        }
        selected_lapp.select();
    }
});


/******************************************************************************/
// main view
LampAppMainView = Backbone.Layout.extend({
    template: "#main-layout",
    
    initialize: function() {
        _(this).bindAll("lapp_selected");
        this.listenTo(this.collection, 'change:selected', this.lapp_selected);
    },

    log: function(msg) {
        console.log('<MAIN_VIEW> '+ msg);
    },

    /* callback when a lapp is selected
    */
    lapp_selected: function(model, value, option) {
        if(value){ // a lapp is selected
            this.log("lapp selected");
            // setup the view
            this.setView("#lapp-editor-view", new Views.LappAceEditorView({
                model: this.collection.selected,
            })).render();
            this.setView("#lapp-run-view", new Views.LappRunView({
                model: this.collection.selected,
            })).render();
        } else { // lapp is un-selected
            this.log("lapp un-selected");
            this.removeView("#lapp-editor-view");
            this.removeView("#lapp-run-view");
        }
    }
});


/******************************************************************************/
BBL.init = function() {
    // common setup
    // Models
    BBL.lapp_collection = new LappCollection();
    BBL.status_model = new LappStatusModel();
    BBL.status_model.fetch();

    // Views
    // setup the main view
    BBL.main_view = new LampAppMainView({
        collection: BBL.lapp_collection,
    });
    var app_body = $("#app");
    app_body.empty();
    BBL.main_view.$el.appendTo(app_body);

    // setup list view
    BBL.main_view.setView("#lapp-list-view", new Views.LappListView({
        collection: BBL.lapp_collection,
    }));

    // setup new lapp view
    BBL.main_view.setView("#new-lapp-view", new Views.NewLappView({
        collection: BBL.lapp_collection,
    }));

    // setup title view
    BBL.main_view.setView("#title-view", new Views.TitleView({
        collection: BBL.lapp_collection,
    }));

    // settupt status view
    BBL.main_view.setView("#lapp-status-view", new Views.LappStatusView({
        model: BBL.status_model,
    }));

    BBL.main_view.render();

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

