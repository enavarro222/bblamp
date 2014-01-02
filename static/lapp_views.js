/*global Backbone, $, _ */
var Views = {};

/******************************************************************************/
/* lapp python code editor (ACE)
*/
Views.LappAceEditorView = Backbone.Layout.extend({
    template: "#lapp-ace-editor",

    log: function(msg) {
        console.log('<ACE_EDITOR:'+ this.model.id + '> '+ msg);
    },

    initialize: function() {
        this.log("init");
        _(this).bindAll('modelChanged', 'updateEditable', 'codeModified', 'setEditorHeight');
        this.listenTo(this.model, 'change:py_code', this.modelChanged);
        this.listenTo(this.model, 'change:from_blockly', this.updateEditable);
    },

    modelChanged: function(model, value, option) {
        if (!_.has(option, 'from') || option.from != this) {
            this.log('code changed from ' + option.from);
            this.editor.setValue(this.model.get('py_code'));
            window.setTimeout(this.setEditorHeight, 50);
        }
    },
    
    updateEditable: function() {
        this.editor.setReadOnly(this.model.get("from_blockly"));
    },
    
    codeModified: function() {
        var new_code = this.editor.getValue();
        this.log("py_code changed !");
        if(!this.model.get("from_blockly")){
            this.model.set(
                {
                    'py_code': new_code,
                },
                {'from': this}
            );
        } else {
            this.log("direct change of py code wheras it is a blockly app")
        }
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
        // set value
        this.editor.setValue(this.model.get('py_code'));
        this.updateEditable();
        this.editor.clearSelection();
        // wait 0.05 sec before that
        window.setTimeout(this.setEditorHeight, 50);
        // bind it
        this.editor.getSession().on('change', this.codeModified);
        this.listenTo(asEvents(window), "resize", this.setEditorHeight);
        return this;
    },
    
    setEditorHeight: function (){
        var lastLine = this.$("#the_ace_editor .ace_gutter-cell:last");
        var neededHeight = lastLine.position().top + lastLine.outerHeight() + 40;
        var minimalHeight = window.innerHeight - $("#head").height() - 40;
        //this.log("change editor height : " + neededHeight + " vs " + minimalHeight);
        neededHeight = Math.max(neededHeight, minimalHeight);
        this.$("#ace_editor_mask").height(neededHeight);
    },
});


/******************************************************************************/
/* lapp blockly code editor (ACE)
*/
Views.LappBlocklyEditorView = Backbone.Layout.extend({
    template: "#lapp-blockly-editor",

    log: function(msg) {
        console.log('<BLK_EDITOR:'+ this.model.id + '> '+ msg);
    },

    initialize: function() {
        this.log("init");
        _(this).bindAll('modelChanged', 'codeModified', 'setEditorHeight');
        this.listenTo(this.model, 'change:by_code', this.modelChanged);
        this.listenTo(this.model, 'change:from_blockly', this.updateEditable);
    },

    /* returns the xml code of the current blockly app */
    getBlocklyCode: function() {
        var xml = Blockly.Xml.workspaceToDom(Blockly.mainWorkspace);
        var xml_text = Blockly.Xml.domToText(xml);
        return xml_text;
    },
    
    setBlocklyCode: function(xml_text) {
        try{
            var xml = Blockly.Xml.textToDom(xml_text);
            Blockly.Xml.domToWorkspace(Blockly.mainWorkspace, xml);
        } catch (error){
            //XXX: manage the error
            this.log(error);
        }
    },
    
    modelChanged: function(model, value, option) {
        if (!_.has(option, 'from') || option.from != this) {
            this.log('code changed from ' + option.from);
            this.setBlocklyCode(this.model.get('by_code'));
            //this.setEditorHeight();
        }
    },
    
    updateEditable: function() {
        Blockly.readOnly = !this.model.get("from_blockly");
    },
    
    codeModified: function() {
        this.log("by_code changed !");
        //TODO: ckeck if realy different
        if(this.model.get("from_blockly")){
            
            var new_code = this.getBlocklyCode();
            this.model.set(
                {
                    'by_code': new_code,
                },
                {'from': this}
            );
        } else {
            // XXX: better error management
            this.log("change blockly code wheras it is not blockly app");
        }
        //this.setEditorHeight();
    },
    
    serialize: function() {
        return {};
    },
    
    afterRender: function(){
        this.log("create the Blockly editor");
        // create the blockly editor
        Blockly.inject(
            document.getElementById('the_blockly_editor'),
            {
                path: './static/blockly/', //TODO: set it with a template
                toolbox: document.getElementById('blockly_toolbox')
            }
        );
        // set the code
        this.updateEditable();
        if(this.model.get('from_blockly')){
            this.setBlocklyCode(this.model.get('by_code'));
        }
        //this.setEditorHeight();
        // bind it
        this.listenTo(
            asEvents(Blockly.mainWorkspace.getCanvas()),
            'blocklyWorkspaceChange',
            this.codeModified
        )
        //this.listenTo(asEvents(window), "resize", this.setEditorHeight);
        return this;
    },
    
    setEditorHeight: function (){
        //XXX need translation
        var lastLine = this.$("#the_ace_editor .ace_gutter-cell:last");
        var neededHeight = lastLine.position().top + lastLine.outerHeight();
        var minimalHeight = window.innerHeight - $("#head").height() - 8;
        //this.log("change editor height : " + neededHeight + " vs " + minimalHeight);
        neededHeight = Math.max(neededHeight, minimalHeight);
        this.$("#ace_editor_mask").height(neededHeight);
    },
});


/******************************************************************************/
/* "Save and Run" lapp view
*/
Views.LappRunView = Backbone.Layout.extend({
    template: "#lapp-run",

    events: {
        "click .bb_save_run": "saveRun",
    },
    
    initialize: function() {
        _(this).bindAll('saveRun');
        this.listenTo(this.model, 'change:state', this.render);
    },

    log: function(msg) {
        console.log('<LAPP_RUN_VIEW:'+ this.model.id + '> '+ msg);
    },

    serialize: function() {
        var data = {};
        data.modified = this.model.isModified();
        data.name = this.model.get("name")
        return data
    },

    saveRun: function() {
        if(this.model.state == "modified"){
            this.log("save !");
            this.model.save();
        }
        this.model.run();
    },
});

/******************************************************************************/
/* lapp menu view
*/
Views.LappMenuView = Backbone.Layout.extend({
    template: "#lapp-menu",

    events: {
        "click .bb_save": "save",
        "click .bb_run": "run",
        "click .bb_close": "close",
    },
    
    initialize: function() {
        _(this).bindAll('save', 'run', 'close');
        this.listenTo(this.model, 'change:state', this.render);
    },

    log: function(msg) {
        console.log('<LAPP_TITLE_VIEW:'+ this.model.id + '> '+ msg);
    },

    serialize: function() {
        var data = this.model.attributes;
        return data
    },

    save: function() {
        if(this.model.isModified()){
            this.log("save !");
            this.model.save();
        }
    },
    
    run: function() {
        if(this.model.state == "modified"){
            this.save();
        }
        this.model.run()
    },
    
    close: function() {
        BBL.router.navigate("/", {trigger: true});
    }
});


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
    
    events: {
    },
    
    initialize: function() {
        this.listenTo(this.collection, 'sync change:selected change:from_blockly change:state', this.render);
    },

    log: function(msg) {
        console.log('<LAPP_LIST_VIEW> ' + msg);
    },

    beforeRender: function() {
        this.log("render");
        this.collection.each(function(model) {
            this.insertView("ul.lapp_list", new Views.LappListItemView({
                model: model,
            }));
        }, this);
        return this;
    },
});

/******************************************************************************/
/* new lapp view
*/
Views.NewLappView = Backbone.Layout.extend({
    keep: true,
    
    template: "#lapp-new",
    
    events: {
        "click button[name=add]": "add",
    },
    
    initialize: function() {
        _(this).bindAll("add");
    },

    log: function(msg) {
        console.log('<NEW_LAPP_VIEW> ' + msg);
    },

    add: function(){
        var appname = this.$('input[name=lapp_name]').val();
        this.log("new app: " + appname);
        if(appname){
            // create a new lapp
            var model = new LappModel({
                name: appname,
                id: appname,
            });
            this.collection.add(model);
            model.save();
        } else {
            //XXX: better msg !
            throw Error("bad name");
        }
    },
});

/******************************************************************************/
/* Lapp Status view
*/
Views.LappStatusView = Backbone.Layout.extend({
    keep: true, // LayoutManager option: the view is not deleted after rendering
    
    template: "#lapp-status",
    
    events: {
        "click .bb_stop": "stop",
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
        //XXX: move to model
        $.ajax("/v1/ctrl/stop");
    },
});

/******************************************************************************/
