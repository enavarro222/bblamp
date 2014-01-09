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

python:
* flask
* gevent >= 1.0 (https://pypi.python.org/pypi/gevent)
* requests
* sseclient (https://pypi.python.org/pypi/sseclient)

javascript:
* jquery
* underscore.js
* backbone.js
* twitter bootstrap
* bootboxjs
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

- [ ] UI: blockly: add "lapp_every_ms"
- [ ] UI: blockly: add "pause of TIME milliseconds"
- [ ] UI: blockly: make "block bags"
- [ ] UI: blockly: add color builder from HSV
- [ ] UI: blockly: i18n automatic load good i18n js file
- [ ] UI: blockly: variables blocs and trunon/turnoff have same color
- [ ] UI: prevent quit without save  **H**
- [ ] UI: add ctrl-s shortcut (save) http://craig.is/killing/mice  **H**
- [ ] UI: run/stop/etc... check ajax call error
- [ ] UI: remove an app (with confirmation)
- [ ] UI: discard changes (with confirmation)
- [ ] UI: (BUG) event may deconect
- [ ] UI: remaster the layout : editor full width, except when simulator on right
- [ ] UI: front page: list of apps in full width
- [ ] UI: unified run/status menu View (with both model = status, collection = lapp_collection)
- [ ] UI: unactivate run when already running ...
- [ ] server: integration with nginx (http://salem.harrache.info/application-wsgi-avec-gevent-et-nginx.html)
- [ ] server: use Flask-Classy ClassView to simplify the API blueprint http://pythonhosted.org/Flask-Classy/
- [ ] server: clean start/stop/status responses (API)
- [ ] server: (BUG) monitoring of msg is not the same than log...
- [ ] server: lapp list alpha order by default
- [ ] lapp: better error message when invalid "lnum"
- [ ] lapp: add a push button (simu first) **H**
- [ ] lapp: add push button (GPIO)
- [ ] lapp: fix issue with GPIO not as root
- [ ] lapp: GPIO how to do with interupt ?
- [ ] lapp: add kill signal catch to lapp, log it correctly before to quit
- [ ] lapp: add i2c sensors
- [ ] lapp: add DHT22 sensors


Long or middle term:
- [ ] server: add the number of connected client in status
- [ ] server: add the **names** of connected client in status
- [ ] server: manage (simply) concurrent edition
- [ ] server: get lapp SyntaxError back to UI
- [ ] UI: manage lapp metadata (author, comment)
- [ ] UI: log & output: manage the history, list, clear
- [ ] UI: use require.js
- [ ] UI: editor ace: autocompletion
- [ ] server: store lapp in a local git repo (so store history)
- [ ] lapp/server: manage hardware (what present, what needed)
- [ ] install a demo version on a public server (with pswd)


- [x] lapp: move to event based ! (every k sec, on button pressed, etc...)
- [x] lapp: reset led on exit
- [x] lapp: lamp start led id at 1 not at 0
- [x] UI: blockly: add a "wait" bloc
- [x] UI: blockly: i18n custom blocks
- [x] UI: blockly: add "setup" block
- [x] UI: blockly: fork => svn export & git add
- [x] UI: update run time in status view
- [x] UI: BUG fix VagueTime 1h hour diff !
- [x] UI: i18n avec i18next
- [x] UI: lapp started time "since" : https://github.com/philbooth/vagueTime.js
- [x] UI: change editor style when readonly
- [x] UI: log & outout popup
- [x] UI: switch between two editors
- [x] UI: change app mode (from_blockly)
- [x] UI: confirmation and error msg with http://bootboxjs.com/
- [x] UI: blockly: **BUG** allow more than one "every" block
- [x] UI: blockly: change all code generation for colors
- [x] UI: blockly: auto-resize
- [x] UI: blockly: first integration (no translation, no save/load)
- [x] UI: blockly: save/load
- [x] UI: blockly: python translation (python read-only)
- [x] UI: blockly: Lapp basic custom block
- [x] UI: blockly: add "count for "i" in ..."
- [x] UI: blockly: change blocks color (more saturation) -> same than bootstrap (cf core/blockly.js:79)
- [x] UI: blockly: add "trun on light ID to color COLOR", "trun off light ID"
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
- [x] server: (BUG) on read log file
- [x] server: manage save
- [x] server: manage .info file
- [x] server: isolate lapp management API in a blueprint, with separete url with version
- [x] server: manage list/new/get/update for lamp app (API)
- [x] UI: basic HTML/JS interface (backbone)x
- [x] UI: add python editor on interface


