#
#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
''' Investigate the WeeWX event handling.'''

import logging

import weewx
import weewx.engine

from weeutil.weeutil import to_bool

VERSION = '0.0.1'

log = logging.getLogger(__name__)
def logdbg(msg):
    """ Log debug level. """
    log.debug(msg)

def loginf(msg):
    """ Log informational level. """
    log.info(msg)

def logerr(msg):
    """ Log error level. """
    log.error(msg)
class EventHandlers(weewx.engine.StdService):
    ''' Save the times and values of the first, last, min, and max of an observation.'''
    def __init__(self, engine, config_dict):
        super(EventHandlers, self).__init__(engine, config_dict)

        service_dict = config_dict.get('AdditionalObservations', {})

        enable = to_bool(service_dict.get('enable', True))
        if not enable:
            loginf("Not enabled, exiting.")
            return

        self.bind(weewx.STARTUP, self.startup)
        self.bind(weewx.PRE_LOOP, self.pre_loop)
        self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)
        self.bind(weewx.CHECK_LOOP, self.check_loop)
        self.bind(weewx.END_ARCHIVE_PERIOD, self.end_archive_period)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        #self.bind(weewx.POST_RECORD_AUGMENTATION, self.post_record_augmentation)
        self.bind(weewx.POST_LOOP, self.post_loop)

    def shutDown(self):
        """Run when an engine shutdown is requested."""
        loginf("Shutting down")

    def startup(self, _event):
        ''' Handle the WeeWX STARTUP event.'''
        loginf("Handling STARTUP event.")

    def pre_loop(self, _event):
        ''' Handle the WeeWX PRE_LOOP event.'''
        loginf("Handling PRE_LOOP event.")

    def new_loop_packet(self, _event):
        ''' Handle the WeeWX NEW_LOOP_PACKET event.'''
        loginf("Handling NEW_LOOP_PACKET event.")

    def check_loop(self, _event):
        ''' Handle the WeeWX CHECK_LOOP event.'''
        loginf("Handling CHECK_LOOP event.")

    def end_archive_period(self, _event):
        ''' Handle the WeeWX END_ARCHIVE_PERIOD event.'''
        loginf("Handling END_ARCHVIE_PERIOD event.")

    def new_archive_record(self, _event):
        '''Handle the WeeWX NEW_ARCHIVE_RECORD event. '''
        loginf("Handling NEW_ARCHIVE_RECORD event.")

    def post_record_augmentation(self, event):
        '''Handle the WeeWX POST_RECORD_AUGMENTATION event. '''
        loginf("Handling POST_RECORD_AUGMENTATION event.")

    def post_loop(self, _event):
        ''' Handle the WeeWX POST_LOOP event.'''
        loginf("Handling POST_LOOP event.")
 