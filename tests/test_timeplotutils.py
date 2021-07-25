#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   Imports:
#   {{{3
import unittest
import argparse
import io
import sys
import importlib
import importlib.resources
import time
import glob
import re
import pprint
import logging
import os
import datetime
import pandas
import dateparser
import matplotlib.pyplot as plt
import pprint
import webbrowser
import tempfile
from subprocess import Popen, PIPE, STDOUT
from io import StringIO
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from matplotlib.dates import DateFormatter
#   }}}1
from timeplot.decaycalc import DecayCalc
from timeplot.timeplot import TimePlot
from timeplot.plotdecayqtys import PlotDecayQtys
from timeplot.plotdassresults import PlotDassResults
from timeplot.util import TimePlotUtils
from timeplot.plottimestamps import PlotTimestamps
#   {{{1

#   debug logging
_log = logging.getLogger('decaycalc')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class Test_DecayCalc(unittest.TestCase):
#   {{{

    def testCalendarRange_Monthly_DateRangeFromFirstAndLast(self):
        dt_start = dateparser.parse("2020-11-18T18:18:31AEDT")
        dt_end = dateparser.parse("2021-01-18T18:18:52AEDT")
        #   {{{
        expected_result = [['2020-11-18', '2020-11-19', '2020-11-20', '2020-11-21', '2020-11-22', '2020-11-23', '2020-11-24', '2020-11-25', '2020-11-26', '2020-11-27', '2020-11-28', '2020-11-29', '2020-11-30'], ['2020-12-01', '2020-12-02', '2020-12-03', '2020-12-04', '2020-12-05', '2020-12-06', '2020-12-07', '2020-12-08', '2020-12-09', '2020-12-10', '2020-12-11', '2020-12-12', '2020-12-13', '2020-12-14', '2020-12-15', '2020-12-16', '2020-12-17', '2020-12-18', '2020-12-19', '2020-12-20', '2020-12-21', '2020-12-22', '2020-12-23', '2020-12-24', '2020-12-25', '2020-12-26', '2020-12-27', '2020-12-28', '2020-12-29', '2020-12-30', '2020-12-31'], ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05', '2021-01-06', '2021-01-07', '2021-01-08', '2021-01-09', '2021-01-10', '2021-01-11', '2021-01-12', '2021-01-13', '2021-01-14', '2021-01-15', '2021-01-16', '2021-01-17', '2021-01-18']]
        #   }}}
        calendar_list = TimePlotUtils.CalendarRange_Monthly_DateRangeFromFirstAndLast(dt_start, dt_end)
        #_log.debug("calendar_list=(%s)" % str(calendar_list))
        self.assertEqual(calendar_list, expected_result)

    #   Continue: 2021-02-12T23:07:45AEDT CalendarRange_Monthly_DateRangeFromFirstAndLast, add optional argument 'partial week' -> start/end first/last lists in list of lists instead of start/end of week (as is default) behaviour
    def testCalendarRange_Weekly_DateRangeFromFirstAndLast_partialweeks(self):
        dt_start = dateparser.parse("2020-11-18T18:18:31AEDT")
        dt_end = dateparser.parse("2021-01-18T18:18:52AEDT")
        #   {{{
        expected_result = [['2020-11-15', '2020-11-16', '2020-11-17', '2020-11-18', '2020-11-19', '2020-11-20', '2020-11-21'], ['2020-11-22', '2020-11-23', '2020-11-24', '2020-11-25', '2020-11-26', '2020-11-27', '2020-11-28'], ['2020-11-29', '2020-11-30', '2020-12-01', '2020-12-02', '2020-12-03', '2020-12-04', '2020-12-05'], ['2020-12-06', '2020-12-07', '2020-12-08', '2020-12-09', '2020-12-10', '2020-12-11', '2020-12-12'], ['2020-12-13', '2020-12-14', '2020-12-15', '2020-12-16', '2020-12-17', '2020-12-18', '2020-12-19'], ['2020-12-20', '2020-12-21', '2020-12-22', '2020-12-23', '2020-12-24', '2020-12-25', '2020-12-26'], ['2020-12-27', '2020-12-28', '2020-12-29', '2020-12-30', '2020-12-31', '2021-01-01', '2021-01-02'], ['2021-01-03', '2021-01-04', '2021-01-05', '2021-01-06', '2021-01-07', '2021-01-08', '2021-01-09'], ['2021-01-10', '2021-01-11', '2021-01-12', '2021-01-13', '2021-01-14', '2021-01-15', '2021-01-16'], ['2021-01-17', '2021-01-18', '2021-01-19', '2021-01-20', '2021-01-21', '2021-01-22', '2021-01-23' ]]
        #   }}}
        #calendar_list = TimePlotUtils.CalendarRange_Weekly_DateRangeFromFirstAndLast(dt_start, dt_end, partialweeks=True)
        self.maxDiff = None
        calendar_list = TimePlotUtils.CalendarRange_Weekly_DateRangeFromFirstAndLast(dt_start, dt_end, arg_expandToFullWeek=True)
        self.assertEqual(calendar_list, expected_result)

    def testCalendarRange_Weekly_DateRangeFromFirstAndLast(self):
        dt_start = dateparser.parse("2020-11-18T18:18:31AEDT")
        dt_end = dateparser.parse("2021-01-18T18:18:52AEDT")
        #   {{{
        expected_result = [['2020-11-15', '2020-11-16', '2020-11-17', '2020-11-18', '2020-11-19', '2020-11-20', '2020-11-21'], ['2020-11-22', '2020-11-23', '2020-11-24', '2020-11-25', '2020-11-26', '2020-11-27', '2020-11-28'], ['2020-11-29', '2020-11-30', '2020-12-01', '2020-12-02', '2020-12-03', '2020-12-04', '2020-12-05'], ['2020-12-06', '2020-12-07', '2020-12-08', '2020-12-09', '2020-12-10', '2020-12-11', '2020-12-12'], ['2020-12-13', '2020-12-14', '2020-12-15', '2020-12-16', '2020-12-17', '2020-12-18', '2020-12-19'], ['2020-12-20', '2020-12-21', '2020-12-22', '2020-12-23', '2020-12-24', '2020-12-25', '2020-12-26'], ['2020-12-27', '2020-12-28', '2020-12-29', '2020-12-30', '2020-12-31', '2021-01-01', '2021-01-02'], ['2021-01-03', '2021-01-04', '2021-01-05', '2021-01-06', '2021-01-07', '2021-01-08', '2021-01-09'], ['2021-01-10', '2021-01-11', '2021-01-12', '2021-01-13', '2021-01-14', '2021-01-15', '2021-01-16'], ['2021-01-17', '2021-01-18', '2021-01-19', '2021-01-20', '2021-01-21', '2021-01-22', '2021-01-23']]
        #   }}}
        calendar_list = TimePlotUtils.CalendarRange_Weekly_DateRangeFromFirstAndLast(dt_start, dt_end)
        self.assertEqual(calendar_list, expected_result)



#   }}}


