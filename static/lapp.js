/*global Backbone, $, _ */
var BBL = {};

/* Router, to select a lapp
*/
var LampAppRouter = Backbone.Router.extend({
    routes: {
        '': 'index',
        ':lapp_name': 'open_lapp',
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
    
    events: {
        "click a.navbar-brand": "index",
    },
    
    initialize: function() {
        _(this).bindAll("lapp_selected", "index");
        this.listenTo(this.collection, 'change:selected', this.lapp_selected);
    },

    log: function(msg) {
        console.log('[main_view] ' + msg);
    },

    index: function(){
        BBL.router.navigate("/", {trigger: true});
    },

    /* callback when a lapp is selected
    */
    lapp_selected: function(model, value, option) {
        if(value){ // a lapp is selected
            this.log("lapp selected");
            // setup the view
            this.setView("#main", new Views.LappEditorsView({
                model: this.collection.selected,
            })).render();
            
            this.setView("#lapp-menu-view", new Views.LappMenuView({
                model: this.collection.selected,
            })).render();

            this.setView("#lapp-run-view", new Views.LappRunView({
                model: this.collection.selected,
            })).render();
        } else { // lapp is un-selected
            this.log("lapp un-selected");
            this.removeView("#main");
            this.removeView("#lapp-menu-view");
            this.removeView("#lapp-run-view");
        }
    }
});


/******************************************************************************/
BBL.init = function(t) {
    // 't' is the i18next translation method
    
    // common setup
    // Models
    BBL.lapp_collection = new LappCollection();
    BBL.status_model = new LappStatusModel();
    BBL.status_model.fetch();

    BBL.simu = new LampSimu.Model()

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

    // setup the form to create new lapp
    BBL.main_view.setView("#new-lapp-view", new Views.NewLappView({
        collection: BBL.lapp_collection,
    }));
    
    //XXX
    BBL.main_view.setView("#led_pixels", new LampSimu.LedPixelsView({
        collection: BBL.simu.leds,
    }));

    // setup status view
    BBL.main_view.setView("#lapp-status-view", new Views.LappStatusView({
        model: BBL.status_model,
    }));
    // setup notification on logs and outputs
    BBL.status_model.logs.on("add", function(model, collection){
        toastr.warning(
            model.get("msg"),
            "",
            {
                "onclick": function(){alert("io")}
            }
        );
    });
    BBL.status_model.outputs.on("add", function(model, collection){
        toastr.info(
            model.get("msg"),
            "",
            {
                "onclick": function(){alert("io")}
            }
        );
    });
    
    // mesage before to quit the page
//    window.onbeforeunload = function() {
//      return "";
//    }
    
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
    // config for notification
    toastr.options = {
      "closeButton": true,
      "debug": false,
      "positionClass": "toast-top-right",
      "showDuration": "300",
      "hideDuration": "1000",
      "timeOut": "10000",
      "extendedTimeOut": "2000",
      "showEasing": "swing",
      "hideEasing": "linear",
      "showMethod": "fadeIn",
      "hideMethod": "fadeOut"
    }
    
    // i18n init
    var i18n_options = {
        detectLngQS: 'lang',
        fallbackLng: 'en',
        resGetPath: 'static/locales/__ns__-__lng__.json',
        debug: true,
    };
    i18n.init(i18n_options, function(t){
        // setup moment (date) language
        moment.lang(i18n.lng().split("-")[0]);
        
        // translate the loading mesage
        $("#app").i18n();
        
        // start the app itself
        BBL.init(t);
    });
});

