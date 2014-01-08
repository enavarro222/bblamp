/******************************************************************************/
/* LampApp model
 * The model for a Lamp Application
 * 
 * not: it is part of a collection
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
        //TODO: manage it by a default attr
        this.set({selected: false}, {silent: true});
        this.changeState('partial', {silent: true});
        this.on('change', this.onChange);
        // attributes that are monitor to change lapp state
        this.saved_attrs = ['py_code', 'by_code', 'from_blockly'];
    },

    select: function() {
        this.collection.select(this);
    },
    
    unselect: function() {
        this.collection.unselect();
    },

    /* update the model state
     * 
     * 'options' are passed to model.set function
     */
    changeState: function(new_state, options) {
        var old_state = this.get("state");
        if(old_state != new_state) {
            this.log('change state from "'+ old_state +'" to "'+ new_state + '"');
            if (_.indexOf(['partial', 'uptodate', 'modified'], new_state) >= 0) {
                this.set({'state': new_state}, options);
            } else {
                throw new Error('Invalide State : ' + new_state);
            }
        }
    },

    isModified: function(){
        return this.get("state") == "modified";
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
    
    // run the lapp (on the server)
    run: function() {
        // TODO: stop first, check callbacks
        var lappName = this.id;
        this.log("*run* : /v1/ctrl/run/" + lappName);
        $.ajax("/v1/ctrl/run/" + lappName);
    },

    //override fetch fct to manage state
    fetch: function(attrs, options) {
        this.log("fetch !");
        var result = Backbone.Model.prototype.fetch.call(this, attrs, options);
        var self = this;
        result.done(function() {
            self.changeState('uptodate');
        });
        return result;
    },

    /* called when the model is changed, update the state
    *  update the model state if one of the saved attribut has changed
    */
    onChange: function() {
        this.log("changed");
        if (this.get('state') != 'partial' &&
                _.intersection(_.keys(this.changedAttributes()), this.saved_attrs).length > 0) {
            this.changeState('modified');
        }
    }
});

/* The collection of LampApp
*/
var LappCollection = Backbone.Collection.extend({
    model: LappModel,
    url: '/v1/lapps',

    initialize: function() {
        this.selected = null;
    },

    unselect: function(){
        if(this.selected != null){
            old_selected = this.selected;
            this.selected = null;
            old_selected.set({selected: false});
        }
    },

    select: function(model) {
        old_selected = this.selected;
        this.selected = model;
        if (old_selected) {
            old_selected.set({selected: false}, {silent: true});
        }
        this.selected.set({selected: true}, {silent: false});
    },

   // The Twitter Search API returns tweets under "results".
    parse: function(response) {
        return response.lapps;
    }
});

/******************************************************************************/
/* LappStatus model
 * The model for the status of the running lapp
 * 
 * also manage the event sent by the server (status changed, log, etc...)
 * 
 */
var LappStatusModel = Backbone.Model.extend({
    url: "/v1/ctrl/status",

    initialize: function(){
        _(this).bindAll("serverEvent");
        // suscribe to server event
        this.evtSrc = new EventSource("/log/subscribe");
        this.evtSrc.onmessage = this.serverEvent
        this.logs = new Backbone.Collection;
        this.outputs = new Backbone.Collection;
    },

    serverEvent: function(event){
        data = JSON.parse(event.data);
        if(!_.has(data, "dtype") || !_.has(data, "data")){
            throw SyntaxError("Server mesage is not correct !");
        }
        switch(data.dtype){
            case "status":
                this.clear({"silent":true});
                this.set(data.data);
                break;
            case "log":
                this.logs.add({"msg":data.data})
                break;
            case "output":
                this.outputs.add({"msg":data.data})
                break;
            default:
                throw SyntaxError("Unknow msg type: '" + data.dtype + "' !");
        }
    },

   // The Twitter Search API returns tweets under "results".
    parse: function(response) {
        response["log"] = [];
        response["output"] = []
        return response;
    },
    
    stop: function(){
        // stop the running app
        //TODO: check the return value
        $.ajax("/v1/ctrl/stop");
    },
    
    isRunning: function(){
        return this.get("status") == "running";
    },
});

