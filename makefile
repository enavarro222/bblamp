
.phony: get-ace install-ace

install: get-ace install-ace
	echo "done";

get-ace:
	git clone https://github.com/ajaxorg/ace-builds.git

install-ace:
	cd static && ln -s ../ace-builds/src-min-noconflict ./ace

get-blockly:
	svn checkout http://blockly.googlecode.com/svn/trunk/ ./blockly

install-blockly:
	cd static && ln -s ../blockly ./

