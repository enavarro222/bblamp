bblamp
======

The idea is to build a lamp that is easily programmable throw a web interface using [blockly](https://code.google.com/p/blockly/) in order to teach programming to childs and people who are a priori not interested in that.

You need a rPy in a nice box connected to a strip of RGB leds, a bunch of sensors and buttons.
Connect it to your local network, and install BBLamp on the rPy.
Then you can navigate to the rPy ip address and start programing it !

Blockly makes programming easy and intuitive, and the lamp (with led and sensors) make it attractive !

**Warning : This project  is not yet usable !**
This project is very young but in (active) development. Feel free to contact me for any question, comments, typo correction or whatever...


Require
------
* flask
* gevent >= 1.0 (https://pypi.python.org/pypi/gevent)
* jquery
* underscore.js
* backbone.js
* ace.js (source code editor)
* blockly


Components
----------

* Raspberry Pi
* string of 25 12mm LedPixels WS2801 (SPI port)
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

- [ ] UI: add lapp button in a proper View
- [ ] UI: manage log and output, list, clean, popup?
- [ ] UI: blockly: first integration (no translation, no save/load)
- [ ] UI: blockly: save/load
- [ ] UI: blockly: python translation (python read-only)
- [ ] UI: blockly: Lapp basic custom block
- [ ] UI: add ctrl-s shortcut (save) http://craig.is/killing/mice
- [ ] UI: check ajax call error
- [ ] UI: add remove an app (with confirmation)
- [ ] UI: better css (twitter bootstrap ?
- [ ] UI: manage lapp metadata
- [ ] UI: front page...
- [ ] UI: reorganise views in different js files
- [ ] server: use Flask-Classy ClassView to simplify the API blueprint http://pythonhosted.org/Flask-Classy/
- [ ] server: clean start/stop/status responses (API)
- [ ] lapp: add kill signal catch to lapp, log it correctly before to quit
- [ ] lapp: test i2c sensors
- [ ] lapp: fix issue with GPIO not as root
- [ ] lapp: how to do with interupt ?
- [ ] lapp: manage start on boot
- [ ] lapp: ledPixel better color management
- [ ] make hardware changeable (pygame, html/js, texte)

- [ ] (cancel) UI: make a model for the UI it self (selectedLapp)
- [ ] (cancel) UI: use good html5 balise : section, header, nav, ... http://stackoverflow.com/questions/4781077/html5-best-practices-section-header-aside-article-tags

- [x] UI: make LappPythonCodeEditor view
- [x] UI: make a LappSaveView
- [x] UI: close a lapp
- [x] UI: make a LappView use sub views (and manage leaks)
- [x] UI: test backbone layout manager plugin
- [x] server: manage save
- [x] server: manage .info file
- [x] server: isolate lapp management API in a blueprint, with separete url with version
- [x] server: manage list/new/get/update for lamp app (API)
- [x] UI: basic HTML/JS interface (backbone)x
- [x] UI: add python editor on interface


