""" Learn about tags. """
import datetime
import time

from weewx.cheetahgenerator import SearchList
from weewx.tags import TimespanBinder
from weeutil.weeutil import TimeSpan

try:
    import weeutil.logger # pylint: disable=unused-import
    import logging

    log = logging.getLogger(__name__) # pylint: disable=invalid-name

    def logdbg(msg):
        """ log debug messages """
        log.debug(msg)

    def loginf(msg):
        """ log informational messages """
        log.info(msg)

    def logerr(msg):
        """ log error messages """
        log.error(msg)

except ImportError:
    import syslog

    def logmsg(level, msg):
        """ log to syslog """
        syslog.syslog(level, 'Belchertown Extension: %s' % msg)

    def logdbg(msg):
        """ log debug messages """
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        """ log informational messages """
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        """ log error messages """
        logmsg(syslog.LOG_ERR, msg)


VERSION = "0.0.1"

class TagLearning(SearchList):
    """ Learn about tags."""
    def __init__(self, generator):
        SearchList.__init__(self, generator)
        self.timespan = None
        self.db_lookup = None
        self.generator = generator

    def get_extension_list(self, timespan, db_lookup):
        self.timespan = timespan
        self.db_lookup = db_lookup

        search_list_extension = {'timeperiod': self.get_time_period,
                                 'getdays': self._get_last_n_days,
                                 'get7days': self._get_last_7_days,
                                 'alltime2': self.all_time
                                }

        return [search_list_extension]

    def get_time_period(self, data_binding=None):
        loginf(data_binding)
        return data_binding

    def _get_last_n_days(self, days, data_binding=None):
        loginf(days)
        loginf(data_binding)
        start_date = datetime.date.fromtimestamp(self.timespan.stop) - datetime.timedelta(days=days)
        start_timestamp = time.mktime(start_date.timetuple())
        last_n_days = TimespanBinder(TimeSpan(start_timestamp, self.timespan.stop),
                                     self.db_lookup,
                                     data_binding = data_binding,
                                     context='last_n_hours',
                                     formatter=self.generator.formatter,
                                     converter=self.generator.converter)

        return last_n_days

    #def _get_last_7_days(self, data_binding=None):
    def _get_last_7_days(self, data_binding=None):
    #def _get_last_7_days(self, data_binding):
        loginf(data_binding)

        #default_archive = self.db_binder.get_manager(default_binding)
        #
        # start_ts = default_archive.firstGoodStamp()
        
        days = 7
        start_date = datetime.date.fromtimestamp(self.timespan.stop) - datetime.timedelta(days=days)
        start_timestamp = time.mktime(start_date.timetuple())
        last_7_days = TimespanBinder(TimeSpan(start_timestamp, self.timespan.stop),
                                     self.db_lookup,
                                     data_binding = data_binding,
                                     context='last_n_hours',
                                     formatter=self.generator.formatter,
                                     converter=self.generator.converter)

        return last_7_days

    def all_time(self, data_binding=None):
        loginf(data_binding)
        dbm = self.db_lookup(data_binding=data_binding)
        start_ts = dbm.firstGoodStamp()
        end_ts = dbm.lastGoodStamp()
        #end_ts = self.report_time
        loginf(start_ts)
        all_time = TimespanBinder(TimeSpan(start_ts, end_ts),
                                   self.db_lookup,
                                   data_binding=data_binding,
                                   context='alltime',
                                   formatter=self.generator.formatter,
                                   converter=self.generator.converter)

        return all_time