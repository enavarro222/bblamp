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


TODO
----
* manage start/stop/status for lamp app (API)
 * only one app may be running at a time
 * stdout/stderr are stored in : "lapp_data/**lapp_name**/**start_time**/**PID**.{stdout, stderr}"
* manage list/new/get/update for lamp app (API)
 * no "database": all metadata are in .py files (module docstring + __author__ + __date__ * ...)
* add blocly interface
