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

class Sleepy(object):
    """Manage the sleeping."""
    def __init__(self, verbosity, seconds, sigterm, sigint, invocation_type):
        self.verbosity = verbosity
        self.seconds = seconds
        self.sigterm = sigterm
        self.sigint = sigint
        self.invocation_type = invocation_type

    def invoke(self, controller):
        if self.invocation_type == "blocking":
            self._invoke_blocking(controller)
        else:
            self._invoke_nonblocking(controller)

    def _invoke_blocking(self, controller):
        loginf("sleeping blocking")

        python_file = os.path.join(os.path.dirname(__file__), 'sleepy.py')
        cmd = ["/usr/bin/python3"]
        cmd.extend([python_file])
        cmd.extend(["--verbosity=%s" % self.verbosity])
        cmd.extend(["--seconds=%s" % self.seconds])
        cmd.extend(["--sigterm=%s" % self.sigterm])
        cmd.extend(["--sigint=%s" % self.sigint])

        try:
            sleepy_cmd = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            stdout = sleepy_cmd.communicate()[0]
            stroutput = stdout.decode("utf-8").strip()
        except Exception as exception:
            logerr(exception)
            raise

        # A negative value -N indicates that the child was terminated by signal N (POSIX only).
        if sleepy_cmd.returncode < 0:
            controller.running = False

        loginf(stroutput)
        loginf(sleepy_cmd.returncode)

        loginf('awake')

    def _invoke_nonblocking(self, controller):
        loginf("sleeping nonblocking")

        python_file = os.path.join(os.path.dirname(__file__), 'sleepy.py')
        cmd = ["/usr/bin/python3"]
        cmd.extend([python_file])
        cmd.extend(["--verbosity=%s" % self.verbosity])
        cmd.extend(["--seconds=%s" % self.seconds])
        cmd.extend(["--sigterm=%s" % self.sigterm])
        cmd.extend(["--sigint=%s" % self.sigint])
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while process.poll() is None and controller.running:
                time.sleep(10)

            if not controller.running and process.poll() is None:
                loginf("attempting TERM")
                process.terminate()

            time.sleep(10)
            if not controller.running and process.poll() is None:
                loginf("attempting KILL")
                process.kill()

            time.sleep(10)
            if process.poll() is None:
                loginf("still running")

            stdout = process.communicate()[0]
            stroutput = stdout.decode("utf-8").strip()
            loginf(stroutput)
        except Exception as exception:
            logerr(exception)
            raise

        loginf('awake')

class TestSignalService(StdService):
    """A service to test handling signals. """
    def __init__(self, engine, config_dict):
        super(TestSignalService, self).__init__(engine, config_dict)

        self.service_dict = config_dict.get('TestSignal', {})

        self.enable = to_bool(self.service_dict.get('enable', True))
        if not self.enable:
            loginf("Not enabled, exiting.")
            return

        sleepy = Sleepy(to_int(self.service_dict.get('verbosity', 0)),
                        to_int(self.service_dict.get('seconds', 10)),
                        self.service_dict.get('sigterm', 'handle'),
                        self.service_dict.get('sigint', 'handle'),
                        self.service_dict.get('type', 'blocking'))

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        self._thread = TestSignalServiceThread(sleepy)
        self._thread.start()

    def new_archive_record(self, event):
        """The new archive record event."""
        self._thread.threading_event.set()

    def shutDown(self):
        """Run when an engine shutdown is requested."""
        loginf("SHUTDOWN - initiated")

        if self._thread:
            loginf("SHUTDOWN - thread initiated")

            if 'start_on_term' in self.service_dict:
                sleepy = Sleepy(0, 10, 'ignore', 'ignore', 'blocking')
                _thread2 = TestSignalServiceThread(sleepy)
                _thread2.start()
                _thread2.threading_event.set()

            self._thread.running = False
            self._thread.threading_event.set()
            self._thread.join(20.0)
            if self._thread.is_alive():
                logerr("Unable to shut down %s thread" %self._thread.name)
            else:
                loginf("SHUTDOWN - thread completed")

            self._thread = None

class TestSignalServiceThread(threading.Thread):
    """A service to test handling signals."""
    def __init__(self, sleepy):
        threading.Thread.__init__(self)

        self.running = False
        self.sleepy = sleepy

        self.threading_event = threading.Event()

    def run(self):
        self.running = True

        self.threading_event.wait() # wait for first event before enterin loop
        while self.running:
            self.sleepy.invoke(self)
            self.threading_event.wait()
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
        self.sleepy = Sleepy(to_int(extras.get('verbosity', 0)),
                             to_int(extras.get('seconds', 10)),
                             extras.get('sigterm', 'handle'),
                             extras.get('sigint', 'handle'),
                             extras.get('type', 'blocking'))

    def run(self):
        loginf("running")
        self.sleepy.invoke(self)

    def finalize(self):
        loginf("finalize")
        super().finalize()

if __name__ == "__main__":
    pass
