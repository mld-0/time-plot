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
    decaycalc = DecayCalc()
    timeplot = TimePlot()

    #   Set True to open output directory in Finder 
    #_flag_openPlots = False

    #_tasklog_dir = os.path.join(os.environ.get('mld_tasklogs'), "_worklog")

    _dassresults_dir = os.environ.get('mld_dass21_results')

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

    prefix = "Schedule.calc."
    postfix = ".vimgpg"

    _test_postfix = "\n"

    _dass_prefix = "dass21-results."
    _dass_postfix = ".vimgpg"

    #   Continue: 2021-01-09T18:10:29AEDT test_AnalyseDataAll
    #   Continue: 2021-01-09T18:12:37AEDT get starttime/timedone from tasklogs, plot alongside data from schedule log file

    def test_ReadDassScoresFromFile(self):
        plotdass = PlotDassResults()
        plotdass._data_path_dir = self._dassresults_dir
        plotdass._data_fname_prefix = self._dass_prefix
        plotdass._data_fname_postfix = self._dass_postfix
        dass_list_data = plotdass._ReadDassData_All()

    def test_ReadDassData_GetFirstAndLastDateInDir(self):
        plotdass = PlotDassResults()
        plotdass._data_path_dir = self._dassresults_dir
        plotdass._data_fname_prefix = self._dass_prefix
        plotdass._data_fname_postfix = self._dass_postfix
        results_list = plotdass._ReadDassData_GetFirstAndLastDateInDir()
        print("results_list=(%s)" % str(results_list))


#   }}}


