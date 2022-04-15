from concurrent.futures import thread
import errno
import os
import subprocess
import time
import threading

import weewx

from weewx.engine import StdService
from weewx.reportengine import ReportGenerator
from weeutil.weeutil import to_bool, to_int

try:
    # Test for new-style weewx logging by trying to import weeutil.logger
    import weeutil.logger
    import logging
    log = logging.getLogger(__name__) # confirm to standards pylint: disable=invalid-name
    def setup_logging(logging_level, config_dict):
        """ Setup logging for running in standalone mode."""
        if logging_level:
            weewx.debug = logging_level

        weeutil.logger.setup('wee_TestSignal', config_dict)

    def logdbg(msg):
        """ Log debug level. """
        log.debug(msg)

    def loginf(msg):
        """ Log informational level. """
        log.info(msg)

    def logerr(msg):
        """ Log error level. """
        log.error(msg)

except ImportError:
    # Old-style weewx logging
    import syslog

    def logmsg(level, msg):
        """ Log the message at the designated level. """
        syslog.syslog(level, 'wee_HealthChecks: %s:' % msg)

    def logdbg(msg):
        """ Log debug level. """
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        """ Log informational level. """
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        """ Log error level. """
        logmsg(syslog.LOG_ERR, msg)

shutting_down = False
def invoke_sleepy2(seconds, sigterm):
    print("sleeping")
    log.info("sleeping")

    python_file = os.path.join(os.path.dirname(__file__), 'sleepy.py')
    cmd = ["/usr/bin/python3"]
    cmd.extend([python_file])
    cmd.extend(["--seconds=%s" % seconds])
    cmd.extend(["--sigterm=%s" % sigterm])

    try:
        sleepy_cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        stdout = sleepy_cmd.communicate()[0]
        stroutput = stdout.decode("utf-8").strip()
    except Exception as e:
        logerr(e)
        raise      

    print(stroutput)  
    log.info(stroutput)

def invoke_sleepy(seconds, sigterm):
    print("sleeping")
    log.info("sleeping")

    python_file = os.path.join(os.path.dirname(__file__), 'sleepy.py')
    cmd = ["/usr/bin/python3"]
    cmd.extend([python_file])
    cmd.extend(["--seconds=%s" % seconds])
    cmd.extend(["--sigterm=%s" % sigterm])
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while process.poll() is None and not shutting_down:
            time.sleep(10)

        if shutting_down and process.poll() is None:
            log.info("attempting TERM")
            process.terminate()
        time.sleep(10)
        if shutting_down and process.poll() is None:
            log.info("attempting KILL")
            process.kill()

        if process.poll() is None:
            log.info("still running")

        stdout = process.communicate()[0]
        stroutput = stdout.decode("utf-8").strip()
    except Exception as e:
        logerr(e)
        raise      

    log.info('awake')

class TestSignalService(StdService):
    """A service to test handling signals. """
    def __init__(self, engine, config_dict):
        super(TestSignalService, self).__init__(engine, config_dict)    

        service_dict = config_dict.get('TestSignal', {})

        self.enable = to_bool(service_dict.get('enable', True))    
        if not self.enable:
            loginf("Not enabled, exiting.")
            return            

        seconds = to_int(service_dict.get('seconds', 10))    
        sigterm = service_dict.get('sigterm', 'handle')  

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        self._thread = TestSignalServiceThread(seconds, sigterm)
        self._thread.start()

    def new_archive_record(self, event):
        """The new archive record event."""
        self._thread.threading_event.set()

    def shutDown(self):
        """Run when an engine shutdown is requested."""
        global shutting_down
        loginf("SHUTDOWN - initiated")

        if self._thread:
            loginf("SHUTDOWN - thread initiated")
            self._thread.running = False
            shutting_down = True
            self._thread.threading_event.set()
            self._thread.join(20.0)
            if self._thread.is_alive():
                logerr("Unable to shut down %s thread" %self._thread.name)

            self._thread = None        

class TestSignalServiceThread(threading.Thread):
    """A service to test handling signals."""
    def __init__(self, seconds, sigterm):
        threading.Thread.__init__(self)

        self.seconds = seconds
        self.sigterm = sigterm
        self.running = False

        self.threading_event = threading.Event()

    def run(self):
        self.running = True

        while self.running:
            self.threading_event.wait()
            invoke_sleepy(self.seconds, self.sigterm)
            self.threading_event.clear()

        loginf("exited loop")

class TestSignalGenerator(ReportGenerator):
    """Class for managing signal test generator."""

    def __init__(self, config_dict, skin_dict, *args, **kwargs):
        """Initialize an instance of TestSignalGenerator"""
        loginf("init")
        weewx.reportengine.ReportGenerator.__init__(
            self, config_dict, skin_dict, *args, **kwargs)

        extras = skin_dict.get('Extras', {})
        self.seconds = to_int(extras.get('seconds', 10))    
        self.sigterm = extras.get('sigterm', 'handle')

    def run(self):
        loginf("running")
        invoke_sleepy(self.seconds, self.sigterm)

    def finalize(self):
        loginf("finalize")
        super().finalize()

if __name__ == "__main__":
    pass