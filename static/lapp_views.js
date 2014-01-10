/*global Backbone, $, _ */
var Views = {};
/******************************************************************************/
/* lapp editors view 
*/
Views.LappEditorsView = Backbone.Layout.extend({
    template: "#lapp-editors",
    
    events: {
        'show.bs.tab a[data-toggle="tab"]': "tabClose",
        'shown.bs.tab a[data-toggle="tab"]': "tabOpen",
    },
    
    initialize: function(){
        _(this).bindAll('tabOpen', 'tabClose');
    },
    
    log: function(msg) {
        console.log('<EDITORS:'+ this.model.id + '> '+ msg);
    },
    
    afterRender: function() {
        if(this.model.get("from_blockly")){
            this.$('.nav-tabs a[href="#lapp-editor-view"]').tab('show');
        } else {
            this.$('.nav-tabs a[href="#lapp-source-editor-view"]').tab('show');
        }
    },
    
    tabClose: function(event) {
        // close if needed
        if(event.relatedTarget) {
            var toclose = $(event.relatedTarget).attr('href');
            this.log("close:" + toclose);
            this.removeView(toclose);
        }
    },
    
    tabOpen: function(event) {
        // open the tab
        var tabid = $(event.target).attr('href');
        this.log("open:" + tabid);
        switch(tabid){
            case "#lapp-editor-view":
                this.setView("#lapp-editor-view", new Views.LappBlocklyEditorView({
                    model: this.model,
                })).render();
                break;
            case "#lapp-source-editor-view":
                this.setView("#lapp-source-editor-view", new Views.LappAceEditorView({
                    model: this.model,
                })).render();
                break;
        };
    },
    
    /*beforeRender: function() {
        this.setView("#lapp-editor-view", new Views.LappBlocklyEditorView({
            model: this.model,
        })).render();
        this.setView("#lapp-source-editor-view", new Views.LappAceEditorView({
            model: this.model,
        })).render();
        return this;
    },*/
});

/******************************************************************************/
/* lapp python code editor (ACE)
*/
Views.LappAceEditorView = Backbone.Layout.extend({
    template: "#lapp-ace-editor",

    events: {
        "dblclick .overlay": "makeEditable",
    },
    
    log: function(msg) {
        console.log('<ACE_EDITOR:'+ this.model.id + '> '+ msg);
    },

    initialize: function() {
        this.log("init");
        _(this).bindAll('modelChanged', 'updateEditable', 'codeModified', 'setEditorHeight', 'makeEditable');
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
    
    // check wheter the code is editable or not and change the view
    updateEditable: function(event) {
        var readonly = this.model.get("from_blockly");
        this.editor.setReadOnly(readonly);
        if(readonly){
            this.$(".overlay").slideDown(event ? 400 : 0); //cmt: if event is undefined (false) it is the initial setup so no annimation
        } else {
            this.$(".overlay").slideUp(event ? 400 : 0);
        }
    },
    
    //TODO: factorize that somewhere else
    // change the model to make the blockly code editable
    makeEditable: function(){
        var self = this;
        bootbox.confirm({
            "title": "Are you sure ?",
            "message":"If you edit directly the python code, you will no more be able to modify the blocks.",
            "callback":function(result) {
                if(result){
                    self.model.set({"from_blockly": false})
                }
            }
        }); 
    },
    
    codeModified: function() {
        var new_code = this.editor.getValue();
        this.log("py_code changed !");
        if(!this.model.get("from_blockly")){
            this.model.set({'py_code': new_code}, {'from': this});
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
        ace.require("ace/ext/language_tools");
        this.editor = ace.edit(this.$('#the_ace_editor')[0]);
        this.editor.setTheme('ace/theme/monokai');
        this.editor.getSession().setMode('ace/mode/python');
        this.editor.getSession().setUseWrapMode(true);
        this.editor.setOptions({
            enableBasicAutocompletion: true
        });
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
        var minimalHeight = window.innerHeight
                - 10 - this.$("#ace_editor_mask").offset().top;
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

    events: {
        "dblclick .overlay": "makeEditable",
    },

    log: function(msg) {
        console.log('<BLK_EDITOR:'+ this.model.id + '> '+ msg);
    },

    initialize: function() {
        this.log("init");
        _(this).bindAll('modelChanged', 'codeModified', 'setEditorHeight', 'updateEditable', 'makeEditable');
        this.listenTo(this.model, 'change:by_code', this.modelChanged);
        this.listenTo(this.model, 'change:from_blockly', this.updateEditable);
        // warning. some binding are done after rendering
    },

    /* returns the xml code of the current blockly app */
    getBlocklyCode: function() {
        var xml = Blockly.Xml.workspaceToDom(Blockly.mainWorkspace);
        var xml_text = Blockly.Xml.domToText(xml);
        return xml_text;
    },
    
    /* générate python code from blocks */
    generatePythonCode: function() {
        var code = Blockly.Python.workspaceToCode();
        return code;
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
    
    // check wheter the code is editable or not and change the view
    updateEditable: function(event) {
        var readonly = !this.model.get("from_blockly");
        Blockly.readOnly = readonly;
        if(readonly){
            this.$(".overlay").slideDown(event ? 400 : 0);
        } else {
            this.$(".overlay").slideUp(event ? 400 : 0);
        }
    },
    
    //TODO: factorize that somewhere else
    // change the model to make the blockly code editable
    makeEditable: function(){
        var self = this;
        bootbox.confirm({
            "title": "Are you sure ?",
            "message":"If you edit the blocks the python code will be lost.",
            "callback":function(result) {
                if(result){
                    self.model.set({"from_blockly": true})
                }
            }
        }); 
    },
    
    codeModified: function() {
        this.log("by_code changed !");
        //TODO: ckeck if realy different
        if(this.model.get("from_blockly")){
            
            var by_code = this.getBlocklyCode();
            var py_code = this.generatePythonCode();
            this.model.set(
                {
                    'by_code': by_code,
                    'py_code': py_code,
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
        this.setEditorHeight();
        //BlocklyApps.init();
        this.log("create the Blockly editor");
        // create the blockly editor
        Blockly.inject(
            document.getElementById('the_blockly_editor'),
            {
                path: './static/blockly/', //TODO: set it with a template
                toolbox: document.getElementById('blockly_toolbox'),
                scrollbars: true,
            }
        );
        // set the code
        this.updateEditable();
        if(this.model.get('from_blockly')){
            this.setBlocklyCode(this.model.get('by_code'));
        }
        // bind it
        this.listenTo(
            asEvents(Blockly.mainWorkspace.getCanvas()),
            'blocklyWorkspaceChange',
            this.codeModified
        )
        this.listenTo(asEvents(window), "resize", this.setEditorHeight);
        return this;
    },
    
    setEditorHeight: function (){
        var minimalHeight = window.innerHeight 
                - 10 - this.$("#blockly_editor_mask").offset().top;
        minimalHeight = Math.max(100, minimalHeight);
        var mask = this.$("#blockly_editor_mask");
        mask.height(minimalHeight+"px")
        var width = mask.width() - 6;
        var height = mask.height() - 6;
        //set new size
        this.log(width + " x " +height);
        var editor = this.$("#the_blockly_editor");
        editor.width(width+"px");
        editor.height(height+"px");
        return
        },
});


/******************************************************************************/
/* "Save and Run" lapp view
*/
Views.LappRunView = i18nLayout.extend({
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
        if(this.model.isModified()){
            this.log("save !");
            this.model.save();
        }
        this.model.run();
    },
});

/******************************************************************************/
/* lapp menu view
*/
Views.LappMenuView = i18nLayout.extend({
    template: "#lapp-menu",

    events: {
        "click .bb_save": "save",
        "click .bb_run": "run",
        "click .bb_close": "close",
    },
    
    initialize: function() {
        var self = this;
        _(this).bindAll('save', 'run', 'close');
        this.listenTo(this.model, 'change:state', this.render);
        this.listenTo(bbMousetrap(true), 'ctrl+s', function(){
            self.save();
            return false;
        });
        this.listenTo(bbMousetrap(true), 'ctrl+e', function(){
            self.run();
            return false;
        });
        this.listenTo(bbMousetrap(true), 'ctrl+q', function(){
            self.close();
            return false;
        });
    },

    log: function(msg) {
        console.log('<LAPP_MENU_VIEW:'+ this.model.id + '> '+ msg);
    },

    serialize: function() {
        var data = this.model.attributes;
        return data
    },

    save: function() {
        if(this.model.isModified()){
            this.model.save();
        }
    },
    
    run: function() {
        this.save();
        this.model.run()
    },
    
    close: function() {
        //XXX: action on the model (unselect)
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
Views.LappStatusView = i18nLayout.extend({
    keep: true, // LayoutManager option: the view is not deleted after rendering
    
    template: "#lapp-status",
    
    events: {
        "click .bb_stop": "stop",
    },
    
    
    initialize: function() {
        _(this).bindAll("stop");
        this.listenTo(this.model, 'change', this.render);
        var self = this;
        this.listenTo(bbMousetrap(true), 'ctrl+a', function(){
            self.stop();
            return false;
        });
    },

    log: function(msg) {
        console.log('<LAPP_STATUS_VIEW> ' + msg);
    },

    serialize: function() {
        this.log("serialize");
        var data = this.model.attributes;
        //var now = new Date(this.model.get("date"));
        var now = new Date();
        if(this.model.isRunning()){
            data.start_from = moment(this.model.get("start_time")).fromNow();
        }
        return data;
    },

    _afterRender: function(){
        // re-render in 30 sec to update start_from timing
        var self = this;
        if(this.model.isRunning()){
            setTimeout(function(){self.render();}, 30*1000);
        }
    },
    
    stop: function(){
        this.model.stop();
    },
});

/******************************************************************************/
