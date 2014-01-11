
.phony: get-ace install-ace build-blockly

install: get-ace install-ace
	echo "done";

get-ace:
	git clone https://github.com/ajaxorg/ace-builds.git

install-ace:
	cd static && ln -s ../ace-builds/src-min-noconflict ./ace

get-bootstrap:
	wget https://github.com/twbs/bootstrap/releases/download/v3.0.3/bootstrap-3.0.3-dist.zip
	unzip bootstrap-3.0.3-dist.zip
	mv dist bootstrap
	rm bootstrap-3.0.3-dist.zip

install-bootstrap:
	cd static && ln -s ../bootstrap ./


get-closure:
	svn checkout http://closure-library.googlecode.com/svn/trunk/ closure-library-read-only

build-blockly:
	cd blockly && python build.py
