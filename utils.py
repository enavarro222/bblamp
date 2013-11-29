#-*- coding:utf-8 -*-
import os
from datetime import datetime

def pid_is_running(pid):
    """
    Return pid if pid is still going.

    >>> import os
    >>> mypid = os.getpid()
    >>> mypid == pid_is_running(mypid)
    True
    >>> pid_is_running(1000000) is None
    True
    """
    try:
        os.kill(pid, 0)
    except OSError:
        return None
    else:
        return pid

def read_lapp_pidfile(pidfile):
    """ Return a dict containing info about the lapp running with the given pid
    file, None if no such file or if the lapp isn't running.
    """
    ret = {}
    if os.path.exists(pidfile):
        with open(pidfile, "r") as pidf:
            try:
                pid = int(pidf.readline().strip())
                if pid_is_running(pid):
                    ret["pid"] = pid
                    ret["script_name"] = pidf.readline().strip()
                    ret["script_dir"] = pidf.readline().strip()
                    ret["start_time"] = pidf.readline().strip()
                else:
                    ret = None
            except ValueError:
                ret = None
    else:
        ret = None
    return ret

def write_lapp_pidfile(pidfile):
    """ Write info about the currently running lapp in a pidfile.
    """
    with open(pidfile, "w") as pidf:
        # pid
        pidf.write("%s\n" % os.getpid())
        import __main__
        main_name = __main__.__file__
        # script name
        pidf.write("%s\n" % os.path.basename(main_name))
        # dir name
        pidf.write("%s\n" % os.path.dirname(os.path.abspath(main_name)))
        # start time
        pidf.write("%s\n" % datetime.now().isoformat())

