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

class Test_PlotTimeStamps(unittest.TestCase):
#   {{{
    decaycalc = DecayCalc()
    timeplot = TimePlot()

    #   Set True to open output directory in Finder 
    _flag_openPlots = True

    _pkg_testdata = "tests.data"
    def _getPath_TestData(self, arg_fname):
    #   {{{
        path_test = None
        with importlib.resources.path(self._pkg_testdata, arg_fname) as p:
            path_test = str(p)
        return path_test
    #   }}}

    #   TODO: 2021-01-18T19:54:13AEDT dedicated test data as test input
    #   Use files created by 'pulse' as test input
    _data_dir_schedule = os.environ.get('mld_logs_pulse')
    _output_dir = os.path.join(tempfile.gettempdir(), "test-decaycalc")
    if not os.path.isdir(_output_dir):
        _log.debug("mkdir _output_dir=(%s)" % str(_output_dir))
        os.mkdir(_output_dir)

    #   Continue: 2021-01-09T18:10:29AEDT test_AnalyseDataAll
    #   Continue: 2021-01-09T18:12:37AEDT get starttime/timedone from tasklogs, plot alongside data from schedule log file

#    if (False):
#        #   {{{
#        def test_PlotDecayQtys_PlotDaily_DecayQtys_ForDateRange(self):
#            dt_start = dateparser.parse("2020-12-18T18:18:31AEDT")
#            dt_end = dateparser.parse("2021-01-18T18:18:52AEDT")
#            plotdecayqtys = PlotDecayQtys()
#            plotdecayqtys.data_file_dir = self._data_dir_schedule
#            plotdecayqtys.data_file_prefix = self.prefix
#            plotdecayqtys.data_file_postfix = self.postfix
#            plotdecayqtys.PlotDaily_DecayQtys_ForDateRange(dt_start, dt_end)
#        #   }}}

    #   Splits/SplitSum tests
    def test_AnalyseVimhSample(self):
        dt_start = dateparser.parse("2021-01-12T18:18:31AEDT")
        dt_end = dateparser.parse("2021-01-17T18:18:52AEDT")
        split = 300
        _vimh_sample_6day = self._getPath_TestData("vimh-6daysample.txt")
        _log.debug("_vimh_sample_6day=(%s)" % str(_vimh_sample_6day))
        plottimestamps = PlotTimestamps()
        #plottimestamps.data_file_prefix = _vimh_sample_6day
        plottimestamps.PlotDaily_TimestampSplits_ForDateRange(_vimh_sample_6day, dt_start, dt_end, split)
        if (self._flag_openPlots):
            webbrowser.open('file:%s' % self._output_dir)

    def test_SampleSplitSums(self):
        pass


#   }}}


