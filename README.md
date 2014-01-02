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
    Warning. you need led drive by WS2801 and **not** WS2811.
    WS2801 strips have 4 wires and can easily be driven by a rPy,
    whereas WS2811 strips have 3 wires and can **not** be driven by a rPy.
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

- [ ] UI: manage log and output, list, clean, pop-up ?
- [ ] UI: switch between two editors
- [ ] UI: blockly: auto-resize
- [ ] UI: blockly: python translation (python read-only)
- [ ] UI: blockly: Lapp basic custom block
- [ ] UI: add ctrl-s shortcut (save) http://craig.is/killing/mice
- [ ] UI: run/stop/etc... check ajax call error
- [ ] UI: run when already running ...
- [ ] UI: add remove an app (with confirmation)
- [ ] UI: manage lapp metadata
- [ ] UI: ace editor: autocompletion
- [ ] UI: (BUG) event may deconect
- [ ] UI: better front page...
- [ ] UI: lapp started time "since" : https://github.com/philbooth/vagueTime.js
- [ ] UI: use require.js
- [ ] server: get SyntaxError
- [ ] server: integration with nginx (http://salem.harrache.info/application-wsgi-avec-gevent-et-nginx.html)
- [ ] server: use Flask-Classy ClassView to simplify the API blueprint http://pythonhosted.org/Flask-Classy/
- [ ] server: clean start/stop/status responses (API)
- [ ] server: manage (simply) concurrent edition
- [ ] server: store lapp in a local git repo (so store history)
- [ ] lapp: move to event based ! (every k sec, on button pressed, etc...)
- [ ] lapp: reset led on exit
- [ ] lapp: add kill signal catch to lapp, log it correctly before to quit
- [ ] lapp: add i2c sensors
- [ ] lapp: add DHT22 sensors
- [ ] lapp: add GPIO button
- [ ] lapp/server: manage hardware (what present, what needed)
- [ ] lapp: fix issue with GPIO not as root
- [ ] lapp: how to do with interupt ?
- [ ] lapp: manage start on boot
- [ ] lapp: ledPixel better color management
- [ ] lapp: make a kivy to develop and test apps when no hardware


- [x] UI: blockly: first integration (no translation, no save/load)
- [x] UI: blockly: save/load
- [x] UI: use twitter bootstrap
- [x] UI: (BUG) ace editor: height error when open a lapp
- [x] UI: reorganise views in a different js file
- [x] UI: integrate backbone-layout in the git repo
- [x] UI: JS lib in a subdir
- [x] UI: add lapp button in a proper View
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


