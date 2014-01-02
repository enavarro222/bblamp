
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

get-bootstrap:
	wget https://github.com/twbs/bootstrap/releases/download/v3.0.3/bootstrap-3.0.3-dist.zip
	unzip bootstrap-3.0.3-dist.zip
	mv dist bootstrap

install-bootstrap:
	cd static && ln -s ../bootstrap ./

