bblamp
======

Very new projet.
The idea is to build a lamp that is programmable by a web interface using blockly (https://code.google.com/p/blockly/).

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
* delete a lapp
* run a lapp
* stop the running lapp
* view which lapp is running (if any)
* view running lapp log (std+err), in live
* view last run(s) log (std+err)
* set a lapp to be run on startup


* no "database": all metadata are in .py files (module docstring + __author__ + __date__ * ...)
* stdout/stderr/status are stored in files ine : "lapp_out"


TODO
----

* isolate lapp management API in a blueprint, with separete url with version
* manage list/new/get/update for lamp app (API)
 - list
 - update_metadata
 - get_metadata
* basic HTML/JS interface (backbone)
 - model lapp
 - model lapp_list
 - model lapp_control
* clean start/stop/status responses (API)
* add kill signal catch to lapp, log it correctly before to quit
* test i2c sensors
* fix issue with GPIO not as root
* how to do with interupt ?
* manage start on boot
* add python editor on interface
    Note: To edit a code in a browser: http://ace.c9.io/
* add blocly interface
* make hardware changeable (pygame, html/js, texte)


