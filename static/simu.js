/******************************************************************************/
var LampSimu = {};

/* Lapp Simu model
 */
LampSimu.Model = Backbone.Model.extend({
    
    initialize: function(){
        _(this).bindAll("serverEvent");
        // suscribe to server event
        this.evtSrc = new EventSource("/simu/v1/subscribe");
        this.evtSrc.onmessage = this.serverEvent
        this.leds = new LampSimu.LedPixelsModel();
    },

    serverEvent: function(event){
        data = JSON.parse(event.data);
        if(!_.has(data, "dtype") || !_.has(data, "data")){
            throw SyntaxError("Server mesage is not correct !");
        }
        switch(data.dtype){
            case "leds":
                this.leds.updateFromArray(data.data)
                break;
            default:
                throw SyntaxError("Unknow msg type: '" + data.dtype + "' !");
        }
    },
});

/*
* one attribute : color = [r, g, b] #
*/
LampSimu.LedModel = Backbone.Model.extend({
    defaults: {
        "color": [0, 0, 0],
    },
    
    initialize: function(){
    },
});

LampSimu.LedPixelsModel = Backbone.Collection.extend({
    model: LampSimu.LedModel,
    //url: '/v1/lapps',

    initialize: function() {
    },

    updateFromArray: function(data){
        // adapt the size
        while(this.size() > _(data).size()){
            this.remove(this.last(), {"silent": true});
        }
        while(this.size() < _(data).size()){
            this.add(new LampSimu.LedModel(), {"silent": true});
        }
        // updates the pixels
        var self = this;
        _.each(data, function(color, index, data){
            if(!_.isEqual(color, self.at(index).get("color"))){
                self.at(index).set({"color":color});
            }
        });
    },
});


LampSimu.LedPixelsView = Backbone.Layout.extend({
    keep: true,
    
    template: "#led-pixels",

    initialize: function() {
        this.listenTo(this.collection, 'change', this.render);
    },
    
    serialize: function() {
        var data = {};
        data.colors = []
        this.collection.forEach(function(model){
            var color = model.get("color");
            data.colors.push(rgbToHex(color[0], color[1], color[2]));
        });
        return data;
    }
});

