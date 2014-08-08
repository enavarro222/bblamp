bblamp
======

BBLamp is a lamp that is easily programmable with the visual and drag and drop language [Blockly](https://code.google.com/p/blockly/).
This project aims at teach programming to childs and people who are a priori not interested in that. Blockly makes programming easy and intuitive, and the lamp (with leds and sensors) make it attractive !

The BBLamp it self is a [Raspberry Pi](http://www.raspberrypi.org/) with a strip of RGB leds, a bunch of sensors and buttons.
It is connected to your local network and is programmable throw a modern and intuitive web interface.

**Warning : This project is not yet fully usable !**  
This project is very young but in (active) development. Feel free to contact me for any question, comments, typo correction or whatever...


Installation
-----------

install depencies:

    $ sudo apt-get install python-pip python-dev
    $ sudo pip insall gevent  # need gevent >= 1.0
    $ sudo pip insall flask
    $ sudo pip insall requests

Note: python-dev are needed to install gevent.

    $ git clone https://github.com/enavarro222/bblamp.git
    $ cd bblamp
    $ make get-ace
    $ make install-ace
    $ make get-bootstrap
    $ make install-bootstrap
    $ run webserver.py

activate SPI on rPy:

    $ sudo vim /etc/modprobe.d/raspi-blacklist.conf
    # add a '#' before line "blacklist spi-bcm2708"

#### TODO :
* install it on a std linux computer without any special hardware
* install it on a rPi with led strip and sensors...

Require (Software)
----------------

for the wimote:

* bluez
* python-cwiid

#### python:
* flask
* gevent >= 1.0 (https://pypi.python.org/pypi/gevent)
* requests
* sseclient (https://pypi.python.org/pypi/sseclient)


#### javascript:
* jquery
* underscore.js
* i18next.js (internationalization)
* backbone.js
* backbone-layoutmanager
* twitter bootstrap
* bootboxjs (for confirmation/alert box)
* toastr (for notifications)
* moment.js (for date/time management)
* mousetrap (for shortcuts)
* ace.js (source code editor)
* blockly


Components (hardware)
-------------------

More comming soon on the prototype hardawre.
For now it is:

* Raspberry Pi
* string of 25 12mm RGB led pixels controlled by WS2801 (SPI)

**Warning.** you need led drive by WS2801 and **not** WS2811. 
WS2801 strips have 4 wires and can easily be driven by a rPi, whereas WS2811 strips have 3 wires and can **not** be driven by a rPi.  You can find it on [ebay](http://www.ebay.com/sch/i.html?_sacat=0&_from=R40&LH_BIN=1&_nkw=WS2801+led&rt=nc&LH_PrefLoc=2).

We aim to add :

* light sensor (i3c)
* humidity and temp sensor (DHT22/AM2302)
* push button
* PIR sensor
* small mic
* small speakers
* wimote

Design, Files and directories
--------------------------

The BBLamp software is organise in three parts :
* the lamp aplications (or "lapp"):
 - created by the users,
 - coded in python, 
 - stored in "user_apps/",
 - based on python modules (hardware drivers ...) which are un "lampapp/".
* edition app:
 - coded in javascript,
 - use Blockly for lamp app creation
 - use ACE for python editing
 - mainly in "static/" and in "templates"
* the webserver:
 - serve the "edition app"
 - manage lapps (Create, Read, Update, Delete, and also: Run, Stop, Status)
 - manage a lamp hardware simulator
 - written in python (with Flask)


The main directories are:

    .
    ├── blockly         # modified version of Blockly
    │   ├── ...
    │   ├── blocks      # contains blocks description
    │   ├── ...
    │   ├── generators  # contains blockscode generator
    │   ├── ...
    │   ├── msg         # contains blockly i18n files
    │   └── ...
    ├── lampapp         # python files for lamp app creation, hardware drivers
    ├── lapp_output     # contains lamp app outputs file (used to communicate with the webserver)
    ├── static          # webapp static files
    │   ├── blockly -> ../blockly # link to blockly
    │   ├── jslib       # bunch of std JS libs
    │   └── locales     # webapp i18n files (use i18next)
    ├── templates       # web app templates (flask templates)
    ├── tests           # ...
    └── user_apps       # contains application created by users


The web server python code is mainly at root level :

    .
    ├── api.py          # flask API to manage lapps
    ├── errors.py       # common lapps management errors
    ├── simulate.py     # lamp hardware simulator API
    ├── static          # static files (ie JS edition app)
    ├── templates       # templates, ie JS edition app main page
    ├── utils.py        # some helpers
    └── webserver.py    # webserer main program

The lapp are based on python modules that are in "lampapp" :
TODO: description of these files 


Lamp app or a "lapp"
------------------

#### some requirements:
* autonomous python program (only depends on "lampapp" module)
* could be written using blockly
* only one running at a time
* is run as a service
* metadata :
 - modification date
 - creation date
 - author
 - comment / description


#### Exemple:
```python
#-*- coding:utf-8 -*-
from lampapp import LampApp
from lampapp.ledpixels import LedPixels

app = LampApp()
app.need("lamp")

@app.setup()
def setup():
    global on
    on = False

@app.every(1)
def loop():
    global on
    # blink
    if on:
        app.lamp.turn_off()
    else:
        app.lamp.turn_on()
    on = not on

if __name__ == "__main__":
    app.run()
```

### Hardware managment

* declare/get "what" is used by a lapp
* declare/get "what" is availble
* (lapp) activate an hardware module
* (ui) load blocks for an hardware module
* (webserer) check if a app may be run or not (hardware available)
* configure hardware (number of led)
* switch between different hardware (simulation or not)


* abstract class : BBLampHarware
 - default attribute name ('lamp', 'wiimote', ...)
* app.need(WiMote)
 - activate the 
* "python ./mylapp.py --list-hardware"

```python
#-*- coding:utf-8 -*-
from lampapp import LampApp

app = LampApp()

# manualy load an hardware driver
from lampapp.ledpixels import LedPixels
app.load("lamp", LedPixels(nb_pixel=32))

app.lamp.on()
```

```python
#-*- coding:utf-8 -*-
from lampapp import LampApp

app = LampApp()
# load a hardware driver which is declared in hardware.conf
app.need("lamp")

app.lamp.on()
```

hardware.conf
```
[lamp]
driver=lampapp.ledpixels.LedPixels
nb_pixel=25
```

hardware.json
```
BBLampHardware = {
    'lamp': {
        'driver':'lampapp.ledpixels.LedPixels',
        'options':{
            'nb_pixel': 25
        },
        ''
    }
}


hardware :
* a python class
* some blocks
* simulation view, server code ?


BBLamp custom blocks
------------------

Here is the description of BBLamp specific blocks.

* setup: run the action when application is run, before everything else.
* every: periodically perform an action.
* wait: make a pause of a given time
* on

For the WiMote:
* start rumble
* stop rumble
* on button {1, 2, A, B, HAUT, BAS, GAUCHE, DROITE} push


lapp web editor/manager
---------------------

#### Features:
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

#### Also some requirements:
* no "database": all metadata are in a .info file
* stdout/stderr/status are redirected in files in the dir : "lapp_out"



TODO
----

- [ ] UI: bug on chrome (at least) short cut don't work after "some time"
- [ ] hard: cleaner power plugs
- [ ] hard: manage DHT22
- [ ] UI: manage loading
- [ ] UI: template JS dans un fichier static ?
- [ ] **H** UI: new lapp (popup with form to choose the name)
- [ ] **H** UI: prevent quit without save
- [x] UI: indicate short cut in UI
- [ ] UI: make lang change view
- [ ] UI: menu to switch to python/blocly
- [ ] UI: rename (popup with form to choose the name) => create delete (if delete fail, then delate new)
- [ ] UI: blockly: add "lapp_every_ms"
- [ ] UI: blockly: add "pause of TIME milliseconds"
- [ ] UI: blockly: make "block bags"
- [ ] UI: blockly: add an HSV color builder
- [ ] UI: blockly: add a block "number of leds"
- [ ] UI: blockly: i18n automatic load good i18n js file
- [ ] UI: blockly: variables blocs and trunon/turnoff have same color
- [ ] UI: run/stop/etc... check ajax call error
- [ ] UI: remove an app (with confirmation)
- [ ] UI: discard changes (with confirmation)
- [ ] UI: (BUG) event may deconect
- [ ] UI: (BUG) when no lapps
- [ ] UI: remaster the layout : editor full width, except when simulator on right
- [ ] UI: clean simulator model (and view)
- [ ] UI: front page: list of apps in full width
- [ ] UI: unified run/status menu View (with both model = status, collection = lapp_collection)
- [ ] UI: unactivate run when already running ...
- [ ] server: integration with nginx (http://salem.harrache.info/application-wsgi-avec-gevent-et-nginx.html)
- [ ] server: use Flask-Classy ClassView to simplify the API blueprint http://pythonhosted.org/Flask-Classy/
- [ ] server: clean start/stop/status responses (API)
- [ ] server: (BUG) monitoring of msg is not the same than log...
- [ ] server: lapp list alpha order by default
- [ ] **H** lapp: add a push button (simu first)
- [ ] lapp: better error message when invalid "lnum"
- [ ] lapp: add push button (GPIO)
- [ ] lapp: fix issue with GPIO not as root
- [ ] lapp: GPIO how to do with interupt ?
- [ ] lapp: add kill signal catch to lapp, log it correctly before to quit
- [ ] lapp: add i2c sensors
- [ ] lapp: add DHT22 sensors
- [ ] lapp: rPy system sensor ? temperature...
  http://raspberrypi.stackexchange.com/questions/357/how-do-i-monitor-and-or-control-the-temperature-of-the-soc
  http://raspberrypi.stackexchange.com/questions/9105/raspberry-pi-onboard-temp-sensors-in-raspbianwheezy


#### Long or middle term:
- [ ] server: add the number of connected client in status
- [ ] server: add the **names** of connected client in status
- [ ] server: manage (simply) concurrent edition
- [ ] server: get lapp SyntaxError back to UI
- [ ] UI: manage lapp metadata (author, comment)
- [ ] UI: log & output: manage the history, list, clear
- [ ] UI: use require.js
- [ ] server: store lapp in a local git repo (so store history)
- [ ] lapp/server: manage hardware (what present, what needed)
- [ ] install a demo version on a public server (with pswd)

#### Done:
- [x] lapp: check color correction
- [x] hard: how many amp for led ? ==> up to 60mA per LED => 1500 mA for 25 leds
- [x] UI: add ctrl-* shortcuts http://craig.is/killing/mice
- [x] UI: editor ace: autocompletion
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

