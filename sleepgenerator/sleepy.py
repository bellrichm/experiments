from logging import logMultiprocessing
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

#signal.signal(signal.SIGTERM, ignoreSIGTERM)
signal.signal(signal.SIGTERM, handleSIGTERM)


log_it("starting")

while running:
    time.sleep(10)

log_it("done")