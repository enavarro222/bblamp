bblamp
======

Very new projet.
The idea is to build a lamp that is programmable by a web interface using blockly (https://code.google.com/p/blockly/).


Components
----------

* Rasbperry Pi
* 12mm LedPixels (string of 25)
* ...


Files and directory
-------------------

* **lapp** : for **l**amp **app**, python module that contains all user defined programs
* todo...


Lamp app
--------

* could be written using blockly
* autonomous python program
* only one running at a time
* may be run as a service
* extends a class, that help

Exemple:
```python
class MyLampApp(LampApp);
   pass

if __name__ == "__main__":
    lapp = MyLampApp()
    lapp.run()

```

Lamp App web editor/manager
---------------------------

* no "database": all metadata are in .py files (module docstring + __author__ + __date__ * ...)
* stdout/stderr are stored in : "lapp_data/**lapp_name**/**start_time**/**PID**.{stdout, stderr}"


TODO
----

- [ ] manage start/stop/status for lamp app (API)
- [ ] manage list/new/get/update for lamp app (API)
- [ ] add blocly interface
