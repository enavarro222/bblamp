/*global Backbone, $, _ */
var BBL = {};
var Views = {};

/******************************************************************************/
//TODO: move to utils.js
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
/******************************************************************************/
/* current lapp view
*/
Views.LappAceEditorView = Backbone.Layout.extend({
    template: "#lapp-ace-editor",

    log: function(msg) {
        console.log('<ACE_EDITOR_VIEW:'+ this.model.id + '> '+ msg);
    },

    initialize: function() {
        this.log("init");
        _(this).bindAll('modelChanged', 'codeModified', 'setEditorHeight');
        this.listenTo(this.model, 'change:py_code', this.modelChanged);
    },

    modelChanged: function(model, value, option) {
        console.log(this.model.changedAttributes())
        if (!_.has(option, 'from') || option.from != this) {
            this.log('code changed from ' + option.from);
            this.editor.setValue(this.model.get('py_code'));
            this.setEditorHeight();
        }
    },
    
    codeModified: function() {
        var new_code = this.editor.getValue();
        this.log("py_code changed !");
        this.model.set({'py_code': new_code}, {'from': this});
        this.setEditorHeight();
    },
    
    serialize: function() {
        var data = this.model.attributes;
        return data
    },
    
    afterRender: function(){
        this.log("create the ACE editor");
        // create the python editor
        this.editor = ace.edit(this.$('#the_ace_editor')[0]);
        this.editor.setTheme('ace/theme/monokai');
        this.editor.getSession().setMode('ace/mode/python');
        this.editor.getSession().setUseWrapMode(true);
        this.editor.setValue(this.model.get('py_code'));
        this.editor.clearSelection();
        // wait 0.05 sec before that
        this.setEditorHeight();
        // bind it
        this.editor.getSession().on('change', this.codeModified);
        this.listenTo(asEvents(window), "resize", this.setEditorHeight);
        return this;
    },
    
    setEditorHeight: function (){
        var lastLine = this.$("#the_ace_editor .ace_gutter-cell:last");
        var neededHeight = lastLine.position().top + lastLine.outerHeight();
        var minimalHeight = window.innerHeight - $("#head").height() - 8;
        //this.log("change editor height : " + neededHeight + " vs " + minimalHeight);
        neededHeight = Math.max(neededHeight, minimalHeight);
        this.$("#ace_editor_mask").height(neededHeight);
    },
});

/* "Save and Run" lapp view
*/
Views.LappRunView = Backbone.Layout.extend({
    template: "#lapp-run",

    events: {
        "click button[name=save]": "saveModel",
        "click button[name=run]": "runLapp",
    },
    
    initialize: function() {
        _(this).bindAll('saveModel', 'runLapp');
        this.listenTo(this.model, 'change:state', this.render);
    },

    log: function(msg) {
        console.log('<LAPP_RUN_VIEW:'+ this.model.id + '> '+ msg);
    },

    serialize: function() {
        var data = this.model.attributes;
        return data
    },

    saveModel: function() {
        this.log("save !");
        this.model.save();
    },
    
    runLapp: function() {
        if(this.model.state == "modified"){
            this.saveModel();
        }
        var lappName = this.model.id;
        this.log("/v1/ctrl/run/" + lappName);
        $.ajax("/v1/ctrl/run/" + lappName);
    },
});

/******************************************************************************/
/* Title lapp list view
*/
Views.TitleView = Backbone.Layout.extend({
    keep: true,
    
    template: "#lapp-title",
    
    initialize: function() {
        this.log("init");
        _(this).bindAll('close');
        this.listenTo(this.collection, 'change:selected change:state', this.render);
    },

    events: {
        'click a.close': 'close',
    },

    log: function(msg) {
        console.log('<TITLE_VIEW>'+ msg);
    },

    serialize: function() {
        data = {};
        if(this.collection.selected){
            data.selected = true;
            data.name = this.collection.selected.id;
        } else {
            data.selected = false;
            data.name = "/* BBLamp */"
        }
        return data;
    },

    close: function() {
        BBL.router.navigate("/", {trigger: true});
    }
});

/******************************************************************************/
/******************************************************************************/
/* Basic lapp list view
*/
Views.LappListItemView = Backbone.Layout.extend({

    //note: the real href is indicated however it is catched by JS
    template: "#lapp-list-item",

    events: {
        'click a': 'click',
    },

    log: function(msg) {
        //console.log('<LAPP_LIST_ITEM_VIEW:'+ this.model.id + '> '+ msg);
    },

    serialize: function() {
        this.log("serialize");
        var data = this.model.attributes;
        return data
    },

    click: function(event) {
        event.preventDefault(); //do not go to the indicated url in the link
        this.log('click on a lappname');
        //this.model.set({selected: true});
        BBL.router.navigate(this.model.get('name'), {trigger: true});
    }
});

/* List of basic lapp view
*/
//XXX: is rendered n times at the begining if there is n lapp
Views.LappListView = Backbone.Layout.extend({
    keep: true, // LayoutManager option: the view is not deleted after rendering
    
    template: "#lapp-list",
    
    initialize: function() {
        this.listenTo(this.collection, 'sync change:selected change:state', this.render);
    },

    log: function(msg) {
       //console.log('<LAPP_LIST_VIEW> '+ msg);
    },

    beforeRender: function() {
        this.log("render");
        this.collection.each(function(model) {
            this.log("add item:" + model.id);
            this.insertView("ul.lapp_list", new Views.LappListItemView({
                model: model,
            }));
        }, this);
    },
});

/******************************************************************************/
/* Lapp Status view
*/
Views.LappStatusView = Backbone.Layout.extend({
    keep: true, // LayoutManager option: the view is not deleted after rendering
    
    template: "#lapp-status",
    
    events: {
        "click button[name=stop]": "stop",
    },
    
    
    initialize: function() {
        _(this).bindAll("stop");
        this.listenTo(this.model, 'change', this.render);
    },

    log: function(msg) {
        console.log('<LAPP_STATUS_VIEW> ' + msg);
    },

    serialize: function() {
        this.log("serialize");
        var data = this.model.attributes;
        
        return data
    },
    
    stop: function(){
        $.ajax("/v1/ctrl/stop");
    },
});


/******************************************************************************/
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
Views.MainView = Backbone.Layout.extend({
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
    BBL.main_view = new Views.MainView({
        collection: BBL.lapp_collection,
    });
    var app_body = $("#app");
    app_body.empty();
    BBL.main_view.$el.appendTo(app_body);

    // setup list view
    BBL.main_view.setView("#lapp-list-view", new Views.LappListView({
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

    // XXX rien a faire ici
    // setup add view
    $('#add').click(function() {
        // create a new lapp
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

