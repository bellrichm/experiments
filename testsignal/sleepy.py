"""Experimenting with signals."""
import argparse
import signal
import syslog
import time

class Sleepy(object):
    """Manage the sleeping."""
    def __init__(self, verbosity, seconds, sigterm, sigint):
        syslog.openlog('wee_sleepy', syslog.LOG_PID | syslog.LOG_CONS)
        self.verbosity = verbosity
        self.seconds = seconds

        self.running = False

        if sigterm == 'ignore':
            signal.signal(signal.SIGTERM, self._ignore_signal)
        else:
            signal.signal(signal.SIGTERM, self._handle_signal)

        if sigint == 'ignore':
            signal.signal(signal.SIGINT, self._ignore_signal)
        else:
            signal.signal(signal.SIGINT, self._handle_signal)

    def _log_it(self, msg):
        syslog.syslog(syslog.LOG_INFO, msg)

    def _ignore_signal(self, signum, _frame):
        self._log_it("Ignoring signal %s (%s)." %(signal.Signals(signum).name, signum)) #pylint bug - pylint: disable=no-member

    def _handle_signal(self, signum, _frame):
        self._log_it("Handling signal %s (%s)." %(signal.Signals(signum).name, signum)) #pylint bug - pylint: disable=no-member
        self.running = False

    def sleep(self):
        """Simulate long running via sleep."""
        self._log_it("starting")

        self.running = True
        while self.running:
            time.sleep(self.seconds)
            if self.verbosity > 0:
                self._log_it("sleeping")

        self._log_it("done")

def main():
    """Mainline code."""
    usage = """sleepy --help
            [--seconds=SECONDS]
            [--sigterm=SIGTERM]
    """

    parser = argparse.ArgumentParser(usage=usage)

    parser.add_argument('--verbosity', dest='verbosity', type=int,
                        help='Controls the logging verbosity.',
                        default=0)
    parser.add_argument('--seconds', dest='seconds', type=int,
                        help='The number of seconds to sleep.',
                        default=10)
    parser.add_argument("--sigterm", choices=["handle", "ignore"],
                        help="How to handle the SIGTERM signal.",
                        default="handle")

    parser.add_argument("--sigint", choices=["handle", "ignore"],
                        help="How to handle the SIGINT signal.",
                        default="handle")

    options = parser.parse_args()

    sleepy = Sleepy(options.verbosity, options.seconds, options.sigterm, options.sigint)
    sleepy.sleep()

if __name__ == "__main__":
    main()
