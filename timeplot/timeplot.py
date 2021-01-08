#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   Imports:
#   {{{3
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
from subprocess import Popen, PIPE, STDOUT
from io import StringIO
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from matplotlib.dates import DateFormatter
#   }}}1
from decaycalc.decaycalc import DecayCalc
#   {{{2
_log = logging.getLogger('decaycalc')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class TimePlot(object):

    #   Continue: 2021-01-03T17:17:49AEST function, for a given month, and a given list of log labels, read all log data for that month, and previous month, then calculate and plot quantities for all given label item for each day in that month
    ##   Given <arguments>, (call methods to) get lists of data from file(s) in arg_data_dir, and return list of calculated qtys remaining for each datetime in arg_dt_list 
    #def CalculateFromFilesRange_Monthly(self, arg_dt_list, arg_data_dir, arg_halflife, arg_onset, arg_file_prefix, arg_file_postfix):
    #    pass

    def AnalyseDataRange(self, arg_data_dir, arg_file_prefix, arg_file_postfix, arg_date_start, arg_date_end, arg_labels_list, arg_halflives_list, arg_onset_lists):
        pass

    #   About: Get a sorted list of the files in arg_data_dir of the form 'arg_file_prefix + %Y-%m + arg_file_postfix' 
    def _GetAvailableFiles_Monthly(self, arg_data_dir, arg_file_prefix, arg_file_postfix):
    #   {{{
        filematches_regex = arg_file_prefix + "[0-9][0-9][0-9][0-9]-[0-9][0-9]" + arg_file_postfix
        filematches_glob = os.path.join(arg_data_dir, filematches_regex)
        _log.debug("filematches_glob=(%s)" % str(filematches_glob))
        filematches_list = glob.glob(filematches_glob)
        filematches_list.sort()
        _log.debug("filematches_list:\n%s" % pprint.pformat(filematches_list))
        return filematches_list
    #   }}}

    def _GetDatetimesFirstAndLast_FromFileList(self, arg_files_list, arg_col_dt, arg_delim):
        datetimes_list = []
        for loop_file in arg_files_list:
            loop_results_dt, loop_results_qty = self._ReadData([ loop_file ], None, arg_col_dt, None, None, arg_delim)
            #datetimes_list.append(loop_results_dt)
            datetimes_list = datetimes_list + loop_results_dt
        datetimes_list.sort()
        #_log.debug("datetimes_list=(%s)" % str(datetimes_list))
        result_dt_first = datetimes_list[0] 
        result_dt_last = datetimes_list[-1] 
        _log.debug("result_dt_first=(%s)" % str(result_dt_first))
        _log.debug("result_dt_last=(%s)" % str(result_dt_last))
        return [ result_dt_first, result_dt_last ]
                

    #   About: Given a list of files, get as a list qtys and datetimes (from columns arg_col_qty and arg_col_dt), for lines where value in column arg_col_label==arg_label (if arg_label is not None, otherwise read every line). Return [ results_dt, results_qty ] lists, sorted chronologicaly 
    def _ReadData(self, arg_files_list, arg_label, arg_col_dt, arg_col_qty, arg_col_label, arg_delim):
    #   {{{
        _log.debug("arg_label=(%s)" % str(arg_label))
        _log.debug("arg_delim=(%s)" % str(arg_delim))
        _log.debug("cols: (dt, qty, label)=(%s, %s, %s)" % (arg_col_dt, arg_col_qty, arg_col_label))
        results_dt = []
        results_qty = []
        for loop_filepath in arg_files_list:
            loop_filestr = self._DecryptGPGFileToString(loop_filepath)
            for loop_line in loop_filestr.split("\n"):
                loop_line_split = loop_line.split(arg_delim)
                #_log.debug("loop_line_split=(%s)" % str(loop_line_split))
                if (arg_label is None) or (loop_line_split[arg_col_label] == arg_label):
                    loop_qty = None
                    if (arg_col_qty is not None):
                        loop_qty_str = loop_line_split[arg_col_qty]
                        loop_qty = Decimal(loop_qty_str)
                    loop_dt_str = loop_line_split[arg_col_dt]

                    loop_dt_str = self._Fix_Datetime_Format(loop_dt_str)

                    loop_dt = dateparser.parse(loop_dt_str)
                    if (loop_dt is None):
                        raise Exception("Failed to parse loop_dt_str=(%s)" % str(loop_dt_str))
                    #_log.debug("loop_dt_str=(%s)" % str(loop_dt_str))
                    #_log.debug("loop_qty=(%s)" % str(loop_qty))
                    #_log.debug("loop_dt=(%s)" % str(loop_dt))
                    results_dt.append(loop_dt)
                    results_qty.append(loop_qty)
        if (len(results_dt) != len(results_qty)):
            raise Exception("mismatch, len(results_dt)=(%s), len(results_qty)=(%s)" % (str(len(results_dt)), str(len(results_qty))))
        _log.debug("len(results)=(%s)" % str(len(results_dt)))
        return [ results_dt, results_qty ]
        #   }}}

    def _Fix_Datetime_Format(self, arg_dt_str):
        #   If datetime is in 'dts' format, i.e: (2021-01-02)-(21-17-11), transform to iso format
        regex_dts = r"\((\d{4}-\d{2}-\d{2})\)-\((\d{2})-?(\d{2})-?(\d{2})\)"
        _match_regex = re.match(regex_dts, arg_dt_str)
        if (_match_regex is not None):
            arg_dt_str = _match_regex.group(1) + "T" + _match_regex.group(2) + ":" + _match_regex.group(3) + ":" + _match_regex.group(4)

        return arg_dt_str

    #   About: plot datetimes and corresponding quantities, and save to given dir with given filename. If current datetime is in datetime range, mark it on plot
    def _PlotResultsForDay(self, arg_result_dt, arg_result_qty, arg_output_dir=None, arg_output_fname=None, arg_markNow=False):
    #   {{{
    #   TODO: 2021-01-04T14:42:45AEST handle multiple lists for arg_result_qty
        from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
        #   Remove timezone from datetimes
        arg_result_dt_nonetzinfo = []
        for loop_dt in arg_result_dt:
            arg_result_dt_nonetzinfo.append(loop_dt.replace(tzinfo=None))
        #   Hide log output for matplotlib
        mpl_logger = logging.getLogger('matplotlib')
        mpl_logger.setLevel(logging.WARNING)
        fig, ax = plt.subplots()
        ax.plot(arg_result_dt_nonetzinfo, arg_result_qty)
        #   If 'now' is between loop_dt[0] and loop_dt[-1], mark it with a dot
        _now = datetime.datetime.now()
        _now_y = 1
        #   If current time is between start/end of arg_result_dt, include point on plot
        if (arg_markNow) and (_now > arg_result_dt_nonetzinfo[0] and _now < arg_result_dt_nonetzinfo[-1]):
            for loop_dt, loop_qty in zip(arg_result_dt_nonetzinfo, arg_result_qty):
                if (loop_dt > _now):
                    _now_y = loop_qty
                    break
            ax.plot([_now], [_now_y], marker='o', markersize=3, color='red')
        myFmt = DateFormatter("%H")
        ax.xaxis.set_major_formatter(myFmt)
#        ax.set_ylim(0, 15)
        ax.set_xlim(arg_result_dt_nonetzinfo[0], arg_result_dt_nonetzinfo[-1])
        ax.xaxis.set_major_locator(MultipleLocator((1/24)))
        ax.yaxis.set_minor_locator(AutoMinorLocator(1))
        fig.autofmt_xdate()
        plt.savefig(os.path.join(arg_output_dir, arg_output_fname + ".png"))
    #   }}}

    #   About: Get a list of the files in arg_data_dir, where each file is of the format 'arg_file_prefix + date_str + arg_file_postfix', and date_str is %Y-%m for each year and month between one month before arg_dt_first, and arg_dt_last
    def _GetFiles_Monthly(self, arg_data_dir, arg_file_prefix, arg_file_postfix, arg_dt_first, arg_dt_last, arg_includeMonthBefore=False):
    #   {{{
        #   Get list of year/month strings for months between arg_dt_first/arg_dt_last, inclusive, plus the month before arg_dt_first
        if (arg_dt_first > arg_dt_last):
            raise Exception("Invalid arg_dt_first=(%s) > arg_dt_last=(%s)" % (str(arg_dt_first), str(arg_dt_last)))
        _dt_format_convertrange = '%Y-%m-%dT%H:%M:%S%Z'
        _dt_format_output = '%Y-%m'
        _dt_freq = 'MS'
        arg_dt_beforeFirst = arg_dt_first
        if (arg_includeMonthBefore):
            arg_dt_beforeFirst = arg_dt_first + relativedelta(months = -1)
        _log.debug("arg_dt_first=(%s)" % str(arg_dt_first))
        _log.debug("arg_dt_beforeFirst=(%s)" % str(arg_dt_beforeFirst))
        _log.debug("arg_dt_last=(%s)" % str(arg_dt_last))
        dt_Range = [ x for x in pandas.date_range(start=arg_dt_beforeFirst.strftime(_dt_format_convertrange), end=arg_dt_last.strftime(_dt_format_convertrange), freq=_dt_freq) ]
        dt_Range_str = [ x.strftime(_dt_format_output) for x in dt_Range ]
        _log.debug("dt_Range=(%s)" % str(dt_Range))
        _log.debug("dt_Range_str=(%s)" % str(dt_Range_str))
        #   Raise exception if arg_data_dir doesn't exist
        if not os.path.isdir(arg_data_dir):
            raise Exception("dir not found arg_data_dir=(%s)" % str(arg_data_dir))
        #   Get list of files of format 'arg_file_prefix + date_str + arg_file_postfix' which exist, with warning for those which don't. Raise exception if no files are found
        located_filepaths = []
        for loop_dt_str in dt_Range_str:
            loop_candidate_filename = arg_file_prefix + loop_dt_str + arg_file_postfix
            loop_candidate_filepath = os.path.join(arg_data_dir, loop_candidate_filename)
            if os.path.isfile(loop_candidate_filepath):
                located_filepaths.append(loop_candidate_filepath)
        _log.debug("located_filepaths:\n%s" % pprint.pformat(located_filepaths))
        if len(located_filepaths) == 0:
            raise Exception("no files located")
        return located_filepaths
        #   }}}

    #   About: Given a path to gpg encrypted file, decrypt file using system gpg/keychain, raise Exception if file is not decryptable, or if it doesn't exist
    def _DecryptGPGFileToString(self, arg_path_file):
    #   {{{
        _log.debug("file=(%s)" % str(os.path.basename(arg_path_file)))
        cmd_gpg_decrypt = ["gpg", "-q", "--decrypt", arg_path_file ]
        p = Popen(cmd_gpg_decrypt, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        result_data_decrypt, result_stderr = p.communicate()
        result_str = result_data_decrypt.decode()
        result_stderr = result_stderr.decode()
        rc = p.returncode
        if (rc != 0):
            raise Exception("gpg decrypt non-zero returncode=(%s), result_stderr=(%s)" % (str(rc), str(result_stderr)))
        _log.debug("lines=(%s)" % str(result_str.count("\n")))
        return result_str
    #   }}}

#   }}}1


