bblamp
======

Very new projet.
The idea is to build a lamp that is programmable throw a web interface using blockly (https://code.google.com/p/blockly/).

Require
------
* flask
* gevent >= 1.0
    (https://pypi.python.org/pypi/gevent)

* jquery
* underscore.js
* backbone.js
* ace.js (source code editor)
* blockly


Components
----------

* Rasbperry Pi
* string of 25 12mm LedPixels (SPI port)
* light sensor (I2C)
* DHT22 
* push button
* PIR sensor
* small mic
* small speakers


Files and directory
-------------------

* **lapp** : for **l**amp **app**, python module that contains all user defined programs
* todo


Lamp app
--------

* could be written using blockly
* autonomous python program
* only one running at a time
* may be run as a service
* extends a class, that help
* metadata :
 - modification date
 - creation date
 - author
 - comment / description


Exemple:
```python
import time

from lapp import LampApp

class MyLampApp(LampApp);
    def setup(self):
        pass

    def loop(self):
        pass
        time.sleep(0.1)

if __name__ == "__main__":
    lapp = MyLampApp()
    lapp.run()

```

Lamp App web editor/manager
---------------------------

* create a new lapp
* edit a lapp directly in python
* edit a lapp with blockly
* delete a lapp (with confirmation)
* run a lapp
* stop the running lapp
* view which lapp is running (if any)
* view running lapp log (std+err), in live
* view last run(s) log (std+err)
* set a lapp to be run on startup

* no "database": all metadata are in a .info file
* stdout/stderr/status are redirected in files in the dir : "lapp_out"


TODO
----

* server: use Flask-Classy ClassView to simplify the API blueprint http://pythonhosted.org/Flask-Classy/
* UI: manage log and output
* UI: add blocly interface
* UI: add ctrl-s shortcut (save)
* UI: check ajax call error
* UI: add remove an app (with confirmation)
* UI: better css
* UI: manage lapp metadata
* UI: front page...
* UI: reorganise views in different js files
* server: clean start/stop/status responses (API)
* lapp: add kill signal catch to lapp, log it correctly before to quit
* lapp: test i2c sensors
* lapp: fix issue with GPIO not as root
* lapp: how to do with interupt ?
* lapp: manage start on boot
* make hardware changeable (pygame, html/js, texte)

* (cancel) UI: make a model for the UI it self (selectedLapp)
* (cancel) UI: use good html5 balise : section, header, nav, ... http://stackoverflow.com/questions/4781077/html5-best-practices-section-header-aside-article-tags

* (ok) UI: make LappPythonCodeEditor view
* (ok) UI: make a LappSaveView
* (ok) UI: close a lapp
* (OK) UI: make a LappView use sub views (and manage leaks)
* (OK) UI: test backbone layout manager plugin
* (OK) server: manage save
* (OK) server: manage .info file
* (OK) server: isolate lapp management API in a blueprint, with separete url with version
* (Ok) server: manage list/new/get/update for lamp app (API)
* (OK) UI: basic HTML/JS interface (backbone)x
* (OK) UI: add python editor on interface


