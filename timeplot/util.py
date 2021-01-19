#   VIM SETTINGS: {{{3
#   vim: set tabstop=4 modeline modelines=10 foldmethod=marker:
#   vim: set foldlevel=2 foldcolumn=3: 
#   }}}1
#   {{{3
import calendar
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
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
#   }}}1
#   {{{2
_log = logging.getLogger('decaycalc')
_logging_format="%(funcName)s: %(levelname)s, %(message)s"
_logging_datetime="%Y-%m-%dT%H:%M:%S%Z"
logging.basicConfig(level=logging.DEBUG, format=_logging_format, datefmt=_logging_datetime)

class TimePlotUtils:

    @staticmethod
    def _GetDaysPerMonthDateRange_FromFirstAndLast(arg_dt_first, arg_dt_last, arg_result_str=True):
    #   {{{
        """Return list of lists 'calendar list', with one list for each month, containing the days of that month falling inside specified date range"""
        if (isinstance(arg_dt_first, str)):
            arg_dt_first = dateparser.parse(arg_dt_first)
        if (isinstance(arg_dt_last, str)):
            arg_dt_last = dateparser.parse(arg_dt_last)
        arg_dt_first = arg_dt_first.replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)
        arg_dt_last = arg_dt_last.replace(tzinfo=None, hour=23, minute=59, second=59)
        _dt_format_output = '%Y-%m-%d'
        calendar_list = []
        months_list = TimePlotUtils._GetMonthlyDateRange_FromFirstAndLast(arg_dt_first, arg_dt_last)
        for loop_month in months_list:
            _log.debug("loop_month=(%s)" % str(loop_month))
            loop_days_in_month = pandas.Period(loop_month).days_in_month
            _log.debug("loop_days_in_month=(%s)" % str(loop_days_in_month))
            loop_days_list = [ x.to_pydatetime() for x in pandas.date_range(start=loop_month, freq='d', periods=loop_days_in_month) ]
            #_log.debug("loop_days_list=(%s)" % str(loop_days_list))
            loop_month_list = []
            for loop_day in loop_days_list:
                if (loop_day >= arg_dt_first) and (loop_day <= arg_dt_last):
                    if (arg_result_str):
                        loop_day = loop_day.strftime(_dt_format_output)
                    loop_month_list.append(loop_day)
            calendar_list.append(loop_month_list)
        return calendar_list
    #   }}}

    @staticmethod
    def _GetMonthlyDateRange_FromFirstAndLast(arg_dt_first, arg_dt_last, arg_includeMonthBefore=False, arg_result_str=True):
    #   {{{
        """Get list of months between two dates, as either strings or datetimes. Optionally include month before first date."""
        if (isinstance(arg_dt_first, str)):
            arg_dt_first = dateparser.parse(arg_dt_first)
        if (isinstance(arg_dt_last, str)):
            arg_dt_last = dateparser.parse(arg_dt_last)
        arg_dt_first = arg_dt_first.replace(day=1, hour=0, minute=0, second=0)
        arg_dt_last = arg_dt_last.replace(day=1, hour=23, minute=59, second=59)
        if (arg_dt_first > arg_dt_last):
            raise Exception("Invalid arg_dt_first=(%s) > arg_dt_last=(%s)" % (str(arg_dt_first), str(arg_dt_last)))
        _dt_format_convertrange = '%Y-%m-%dT%H:%M:%S%Z'
        _dt_format_output = '%Y-%m'
        _dt_freq = 'MS'
        _log.debug("arg_includeMonthBefore=(%s)" % str(arg_includeMonthBefore))
        if (arg_includeMonthBefore):
            arg_dt_beforeFirst = arg_dt_first + relativedelta(months=-1)
            arg_dt_beforeFirst = arg_dt_beforeFirst.replace(day=1)
            arg_dt_first = arg_dt_beforeFirst
        #_log.debug("arg_dt_first=(%s)" % str(arg_dt_first))
        #_log.debug("arg_dt_last=(%s)" % str(arg_dt_last))
        dt_Range = [ x.to_pydatetime() for x in pandas.date_range(start=arg_dt_first.strftime(_dt_format_convertrange), end=arg_dt_last.strftime(_dt_format_convertrange), freq=_dt_freq) ]
        if (arg_result_str):
            dt_Range_str = [ x.strftime(_dt_format_output) for x in dt_Range ]
            _log.debug("dt_Range_str=(%s)" % str(dt_Range_str))
            return dt_Range_str
        else:
            _log.debug("dt_Range=(%s)" % str(dt_Range))
            return dt_Range
    #   }}}

    @staticmethod
    def _GetFiles_FromMonthlyRange(arg_data_dir, arg_file_prefix, arg_file_postfix, arg_dt_first, arg_dt_last, arg_includeMonthBefore=False):
    #   {{{ 
        """Get a list of the files in arg_data_dir, where each file is of the format 'arg_file_prefix + date_str + arg_file_postfix', and date_str is %Y-%m for each year and month between one month before arg_dt_first, and arg_dt_last"""
        dt_Range_str = TimePlotUtils._GetMonthlyDateRange_FromFirstAndLast(arg_dt_first, arg_dt_last, arg_includeMonthBefore, True)
        #   Raise exception if arg_data_dir doesn't exist
        if not os.path.isdir(arg_data_dir):
            raise Exception("dir not found arg_data_dir=(%s)" % str(arg_data_dir))
        #   Get list of files of format 'arg_file_prefix + date_str + arg_file_postfix' which exist, with warning for those which don't. Raise exception if no files are found
        located_filepaths = []
        for loop_dt_str in dt_Range_str:
            loop_candidate_filename = arg_file_prefix + loop_dt_str + arg_file_postfix
            _log.debug("loop_candidate_filename=(%s)" % str(loop_candidate_filename))
            loop_candidate_filepath = os.path.join(arg_data_dir, loop_candidate_filename)
            if os.path.isfile(loop_candidate_filepath):
                located_filepaths.append(loop_candidate_filepath)
        _log.debug("located_filepaths:\n%s" % pprint.pformat(located_filepaths))
        if len(located_filepaths) == 0:
            raise Exception("no files located")
        return located_filepaths
    #   }}}

    @staticmethod
    def _CopyData_DivideByMonth(arg_source_path, arg_dest_dir, arg_dest_prefix, arg_dest_postfix, arg_dt_first, arg_dt_last, arg_overwrite=False, arg_includeMonthBefore=False, arg_gpg_key=None):
    #   {{{
        """Copy lines from single source file arg_source_path to file(s) in arg_dest_dir, for range of months, copying lines containing given month to destination file for said month. Optionally encrypt data with system gpg."""
        dt_Range_str = TimePlotUtils._GetMonthlyDateRange_FromFirstAndLast(arg_dt_first, arg_dt_last, arg_includeMonthBefore, True)
        for loop_dt_str in dt_Range_str:
            loop_data = ""
            with open(arg_source_path, "r") as f:
                for loop_line in f:
                    loop_line = loop_line.strip()
                    #   If loop_line contains loop_dt_str, append it to loop_data
                    if not loop_line.find(loop_dt_str) == -1:
                        loop_data += loop_line + '\n'
            _log.debug("loop_dt_str=(%s) lines(loop_data)=(%s)" % (str(loop_dt_str), len(loop_data.split('\n'))))
            loop_dest_filename = arg_dest_prefix + loop_dt_str + arg_dest_postfix
            loop_dest_filepath = os.path.join(arg_dest_dir, loop_dest_filename)
            _log.debug("loop_dest_filename=(%s)" % str(loop_dest_filename))
            if os.path.isfile(loop_dest_filepath) and not arg_overwrite:
                _log.debug("skip write, arg_overwrite=(%s)" % str(arg_overwrite))
                return 
            if not (arg_gpg_key is None):
                #   TODO: 2021-01-11T18:46:45AEDT if hash of loop_data matches hash of decrypted contents of loop_dest_filepath, skip write
                #loop_data_enc = self._GPGEncryptString2ByteArray(loop_data, arg_gpg_key, False)
                loop_data_enc = TimePlotUtils._GPGEncryptString2ByteArray(loop_data, arg_gpg_key, False)
                with open(loop_dest_filepath, "wb") as f:
                    f.write(loop_data_enc)
            else:
                with open(loop_dest_filepath, "w") as f:
                    f.write(loop_data)
    #   }}}

    @staticmethod
    def _GetAvailableFiles_FromMonthlyRange(arg_data_dir, arg_file_prefix, arg_file_postfix):
    #   {{{
        """Get a sorted list of all files in arg_data_dir of the form 'arg_file_prefix + %Y-%m + arg_file_postfix'"""
        filematches_regex = arg_file_prefix + "[0-9][0-9][0-9][0-9]-[0-9][0-9]" + arg_file_postfix
        filematches_glob = os.path.join(arg_data_dir, filematches_regex)
        _log.debug("filematches_glob=(%s)" % str(filematches_glob))
        filematches_list = glob.glob(filematches_glob)
        filematches_list.sort()
        _log.debug("filematches_list:\n%s" % pprint.pformat(filematches_list))
        return filematches_list
    #   }}}

    @staticmethod
    def _Fix_DatetimeStr(arg_dt_str):
    #   {{{
        """If datetime string is in 'dts' format, i.e: '(2021-01-02)-(21-17-11)' or '(2021-01-02)-(2117-11)', transform to iso format '2021-01-02T21:17:11', otherwise return as-is"""
        regex_dts = r"\((\d{4}-\d{2}-\d{2})\)-\((\d{2})-?(\d{2})-?(\d{2})\)"
        _match_regex = re.match(regex_dts, arg_dt_str)
        if (_match_regex is not None):
            arg_dt_str = _match_regex.group(1) + "T" + _match_regex.group(2) + ":" + _match_regex.group(3) + ":" + _match_regex.group(4)
        return arg_dt_str
    #   }}}

    @staticmethod
    def _GPGEncryptString2ByteArray(text_str, gpg_key_id, flag_ascii_armor=False):
    #   {{{
        """Take a string, encrypt that string with the system gpg keychain, and return result as a bytearray"""
        t_start = time.time()
        #   convert string(text_str) -> bytearray(cmd_encrypt_input)
        cmd_encrypt_input = bytearray()
        cmd_encrypt_input.extend(text_str.encode())
        #   gpg encrypt arguments
        cmd_gpg_encrypt = [ "gpg", "-o", "-", "-q", "--encrypt", "--recipient", gpg_key_id ]
        if (flag_ascii_armor == True):
            cmd_gpg_encrypt.append("--armor")
        #   Use Popen, call cmd_gpg_encrypt, using PIPE for stdin/stdout/stderr
        p = Popen(cmd_gpg_encrypt, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        result_data_encrypt, result_stderr = p.communicate(input=cmd_encrypt_input)
        result_stderr = result_stderr.decode()
        rc = p.returncode
        if (rc != 0):
            raise Exception("Failed to encrypt, rc=(%s)" % str(rc))
        t_end = time.time()
        t_elapsed = round(t_end - t_start, 2)
        #   printdebug:
        _log.debug("encrypt dt=(%s)" % (str(t_elapsed)))
        _log.debug("cmd_gpg_encrypt=(%s)" % str(cmd_gpg_encrypt))
        _log.debug("result_stderr=(%s)" % str(result_stderr))
        _log.debug("text_str_len=(%s)" % str(len(text_str)))
        _log.debug("result_data_encrypt_len=(%s)" % str(len(result_data_encrypt)))
        return result_data_encrypt
    #   }}}

    @staticmethod
    def _GPGDecryptFileToString(arg_path_file):
    #   {{{
        """Given a path to gpg encrypted file, decrypt file using system gpg/keychain, raise Exception if file is not decryptable, or if it doesn't exist"""
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

    @staticmethod
    def DivideList(l, n):
    #   {{{
        """Yield n number of sequential chunks from l. (Use list() on result to convert to list)"""
        d, r = divmod(len(l), n)
        for i in range(n):
            si = (d+1)*(i if i < r else r) + d*(0 if i < r else i - r)
            yield l[si:si+(d+1 if i < r else d)]
    #   }}}

    @staticmethod
    def _DayStartAndEndTimes_FromDate(arg_day):
    #   {{{
        """For a given date, return as python datetime [ first, last ] second of that day"""
        if not isinstance(arg_day, datetime.datetime):
            arg_day = dateparser.parse(arg_day)
        result_start = arg_day.replace(hour=0, minute=0, second=0, microsecond=0)
        result_end = arg_day.replace(hour=23, minute=59, second=59, microsecond=0)
        return [ result_start, result_end ]
    #   }}}
    

#   }}}1

