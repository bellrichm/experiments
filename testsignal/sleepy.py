import argparse
import signal
import syslog
import time

running = True

def log_it(msg):
    #print(msg)
    syslog.syslog(syslog.LOG_INFO, msg)

def ignoreSIGTERM(signum, _frame):
    log_it("Ignoring signal TERM (%s)." %signum)

def handleSIGTERM(signum, _frame):
    global running
    log_it("Handling signal TERM (%s)." %signum) 
    running = False   

usage = """sleepy --help
        [--seconds=SECONDS]
        [--sigterm=SIGTERM]
"""

parser = argparse.ArgumentParser(usage=usage)

parser.add_argument('--seconds', dest='seconds', type=int,
                    help='The number of seconds to sleep.',
                    default=10)
parser.add_argument("--sigterm", choices=["handle", "ignore"],
                    help="How to handle the SIGTERM signal.",
                    default="handle")

options = parser.parse_args()


if options.sigterm == 'ignore':
    signal.signal(signal.SIGTERM, ignoreSIGTERM)
else:
    signal.signal(signal.SIGTERM, handleSIGTERM)

log_it("starting")

while running:
    time.sleep(10)

log_it("done")