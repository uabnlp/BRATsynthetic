import random
import re
import os

from .Maker import Maker
from .. import BratSyntheticConfig


class DateMaker(Maker):

    def __init__(self, config: BratSyntheticConfig):
        super().__init__(config)
        self.days_of_week_long = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                                  'Thurday', 'satruday']
        self.days_of_week_short = ['mon', 'tues?', 'wen', 'wed', 'thur?', 'thr', 'thurs', 'fri', 'sat', 'sun', 'weds']
        self.days_of_week_letter = ['M', 'T', 'Tu', 'W', 'Th', 'R', 'F', 'S', 'Sa', 'Sat', 'A', 'Su']
        self.months_long = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                            'septemeber',
                            'October', 'November', 'December', 'Decemlber']

        self.seasons = ['spring', 'summer', 'fall', 'winter']
        self.months_short = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept?', 'oct', 'nov', 'dec']

        self.holidays = ['New Year\'s', 'New Year\'s Eve', 'Memorial Day', 'Independence Day', 'Labor Day',
                         'Thanksgiving', 'Christmas\.?', 'new years', 'New Years Eve', 'NYE', 'Ramadan']

    def fake_date_wrapper(self, pattern: str = "%Y-%m-%d", end_datetime= None) -> str:
        """
        Get a date string between January 1, 1970 and now
        Uses date method from faker, by on Windows OS machines replaces %- in pattern strings with %.
        strftime on windows does not support %-d, %-m, %-H, ...
        :param pattern: format
        :example: '2008-11-27'
        """
        if os.name == 'nt':
            pattern = pattern.replace('%-', '%')
        return self.fake.date(pattern)

    def regex_from_date_pattern(self, date_pattern: str):

        month_short_regex = '(' + '|'.join(self.months_short) + ')'
        month_long_regex = '(' + '|'.join(self.months_long) + ')'
        days_of_week_short_regex = '(' + '|'.join(self.days_of_week_short) + ')'
        days_of_week_long_regex = '(' + '|'.join(self.days_of_week_long) + ')'
        days_of_week_letter_regex = '(' + '|'.join(self.days_of_week_letter) + ')'
        seasons_regex = '(' + '|'.join(self.seasons) + ')'
        holidays_regex = '(' + '|'.join(self.holidays) + ')'

        regex = date_pattern.replace('.', r'\.')
        regex = regex.replace('%a', days_of_week_short_regex)

        regex = regex.replace('%A', days_of_week_long_regex)

        regex = regex.replace('%w', r'[0-6]')

        regex = regex.replace('%d', r'[0-3]\d')
        regex = regex.replace('%-d', r'[1-3]?\d')

        regex = regex.replace('%m', r'[0-1]\d')
        regex = regex.replace('%-m', r'[1]?\d')

        regex = regex.replace('%b', month_short_regex)
        regex = regex.replace('%B', month_long_regex)

        regex = regex.replace('%y', r'\d{2}')
        regex = regex.replace('%Y', r'\d{4}')

        regex = regex.replace('%H', r'[012]\d{1}')
        regex = regex.replace('%-H', r'[12]?\d{1}')

        regex = regex.replace('%I', r'[01]\d{1}')
        regex = regex.replace('%-I', r'[1]?\d{1}')

        regex = regex.replace('%p', r'([AP]M|[ap]m')

        regex = regex.replace('%M', r'[0-5]\d')
        regex = regex.replace('%S', r'[0-5]\d')

        regex = regex.replace('%f', r'\d{6}')

        ##################
        # CUSTOM PATTERNS
        #
        regex = regex.replace('%.p', r'([AP].M.|[ap].m.')  # Looks for period
        regex = regex.replace('%C', holidays_regex)  # Look for Holidays
        regex = regex.replace('%.d', r'([0-3]\d(st|nd|rd|th))')
        regex = regex.replace('%.-d', r'([0-3]?\d(st|nd|rd|th))')
        regex = regex.replace('%>S', seasons_regex)

        return regex

    def fake_date(self, pattern: str) -> str:

        pattern = pattern.replace('%.d', '%d__NUM_SUFFIX__')
        pattern = pattern.replace('%.-d', '%-d__NUM_SUFFIX__')
        pattern = pattern.replace('%>S', random.choice(self.seasons))

        output = self.fake_date_wrapper(pattern)

        if '__NUM_SUFFIX__' in output:
            index = output.index('__NUM_SUFFIX__')
            if output[index-1] == '1':
                output = output.replace('__NUM_SUFFIX__', 'st')
            elif output[index-1] == '2':
                output = output.replace('__NUM_SUFFIX__', 'nd')
            elif output[index-1] == '3':
                output = output.replace('__NUM_SUFFIX__', 'rd')
            else:
                output = output.replace('__NUM_SUFFIX__', 'th')

        return output

    def fake_holiday(self):
        fake_holidays = ['New Year\'s', 'Memorial Day', 'Independence Day', 'Labor Day', 'Thanksgiving', 'Christmas',
                         'Ramadan']
        return random.choice(fake_holidays)

    def fake_season(self):
        return random.choice(self.seasons)

    def make_one(self, input: str) -> str:
        output = 'UNMATCHED'

        month_short_regex = '(' + '|'.join(self.months_short) + ')'
        month_long_regex = '(' + '|'.join(self.months_long) + ')'
        days_of_week_short_regex = '(' + '|'.join(self.days_of_week_short) + ')'
        days_of_week_long_regex = '(' + '|'.join(self.days_of_week_long) + ')'
        days_of_week_letter_regex = '(' + '|'.join(self.days_of_week_letter) + ')'

        dict_patterns = {
            r'\s+\d{4}': '%B %Y',

            r'\s+\d{,2},\s+\d{4}': '%B %-d, %Y',

            r' 1?\d': '%B %-d',

            r' of \d{4}': '%B of %Y',  # September of 2080

            r' \d\d\d\d': '%b %Y',

            r' 1?\d, \d{4}': '%b %-d, %Y',

            r' [0]\d, \d{2}': '%b %d, %y',

            r' [123]\d, \d{2}': '%b %-d, %y',

            r', \d{2}': '%b, %y',

            r' 0\d, \d{4}': '%b %d, %Y',

            r' \d{,2}, \d{4}': '%b %-d, %Y',

            r'\. \d{4}': '%b. %Y',

            r'': '%b',

            r'of \d{4}': '%b of %Y',  # Sept of 2080

            r'(20|19|21)[0-9][0-9]': '%Y',  # --> Fake.Date()

            r'(20|19|21)[0-9][0-9].': '%Y.',

            r'\d{2}': '%y',  # 06

            r'\d{4}-\d{2}-\d{2}': '%Y-%m-%d',

            r'\d{2}-\d{2}-\d{2}': '%m-%d-%y',

            r'\d{,2}-\d{,2}-\d{2}': '%-m-%-d-%y',

            r'1?\d-1?\d$': '%m-%-d',

            r'\d\d?/ \d{2}': '%-m/ %y',

            r'[01]\d-[0123]\d$': '%m-%d',

            r'\d+/\d+/\d{2}$': '%m/%d/%y',

            r'\d+/\d+/\d{4}': '%m/%d/%Y',

            r'\d+-\d+-\d{4}': '%m-%d-%Y',

            r'[01]?\d/\d{1,2}$': '%m/%d',

            r'[01]?\d/\d{4}': '%m/%Y',

            r's': '%As',  # Thursdays

            r"%b\"": r"%b\"",  # Feb

            r'%-m/%-d/%Y.': r'%-m/%-d/%Y.',  # 1/12/2020.

            r"%-m-%y": r"%-m-%y",  # 11-70

            r"%m/%d/": r"%m/%d/",  # 07/28/

            r"%-m/ %Y": r"%-m/ %Y",  # 4/ 2064

            r"%B %y": r"%B %y",  # July O2

            r"%B %-d,%Y": r"%B %-d,%Y",  # March 25,2064

            r"%b%d%Y": r"%b%d%Y",  # dec142019

            r"%b %-d,%Y.": r"%b %-d,%Y.",  # Jan 6,2020.

            r"%m-%d -%y": r"%m-%d -%y",  # 12-21 -97

            r"%B of  %Y": r"%B of  %Y",  # April of  2096

            r"%B of %y": r"%B of %y",  # November of 73

            r"%-m.%-d.%y": r"%-m.%-d.%y",  # 3.23.64

            r"%B %.-d": r"%B %.-d",  # August 30th

            r"%d %b %Y": r"%d %b %Y",  # 07 Apr 2113

            r"%A %-m/%-d/%y": r"%A %-m/%-d/%y",  # Saturday 7/28/91

            r"%A, %B %-d": r"%A, %B %-d",  # Friday, June 19

            r"%A %B %-d": r"%A %B %-d",  # Wednesday June 21

            r"%a %-m/%-d": r"%a %-m/%-d",  # Wed 12/1

            r"%A, %b %d, %Y": r"%A, %b %d, %Y",  # Tuesday, Apr 27, 2073

            r"%A, %B %d, %Y": r"%A, %B %d, %Y",  # Tuesday, October 01, 2074

            r"%b/%y": r"%b/%y",  # aug/82

            r"%b%d": r"%b%d",  # jan30

            r"%b-%Y": r"%b-%Y",  # Nov-2078

            r"%B. %Y": r"%B. %Y",  # September. 2092

            r"%b. %d, %Y": r"%b. %d, %Y",  # Jan. 24, 2094

            r"%>S, %Y": r"%>S, %Y",  # spring, 2081

            r"%.-d of %B": r"%.-d of %B",  # 12th of September

            r"the %.-d": r"the %.-d",  # the 31st

            r" % B % y": r" % B % y",  # june77

            r"%-m/%-d,%y": r"%-m/%-d,%y",  # 1/10,77

            r"%-m-%-d": r"%-m-%-d",  # 1-24

            r"%d/%m": r"%d/%m",  # 21/05

            r"%B %d %Y": r"%B %d %Y",  # September 24 2132

            r"%b. %d": r"%b. %d",  # Feb. 02

            r"%d %B %y": r"%d %B %y",  # 31 August 41

            r"%d %b %y": r"%d %b %y",  # 26 Jun 92

            r"%>S %Y": r"%>S %Y",  # spring 2090

            r"%>S of %Y": r"%>S of %Y",  # spring of 2094

            r"%>S of %y": r"%>S of %y",  # Fall of 77

            r"Fall %m/%d": r"Fall %m/%d",  # Fall 12/28

            r"%B ‘%y": r"%B ‘%y",  # March '72

            r"%b ‘%y": r"%b ‘%y",  # Oct '64

            r"%b. ‘%y": r"%b. ‘%y",  # Oct. '94

            r"%-m/'%y": r"%-m/'%y",  # 2/'95

            r'%m.%d.%y': r'%m.%d.%y',  # 04.15.94

            r'%B %.d, %Y': r'%B %.d, %Y',  # May 09th, 2092

            r'%B %.-d, %Y': r'%B %.-d, %Y',  # May 9th, 2092

            r'%b %.-d %Y': r'%b %.-d %Y',  # Dec 8th 2019

            r'%d%b%y': r'%d%b%y',  # 30Aug71

            r'%b. %-d': r'%b. %-d',  # Nov. 10

            r'%b %-d.': r'%b %-d.',  # feb 15.

            r'%B %-d.': r'%B %-d.',  # december 26th.

            r'%A, %B %-d, %Y': r'%A, %B %-d, %Y',  # Thursday, February 20, 2089

            r'%d %B %Y': r'%d %B %Y',  # 09 September 2083

            r'%-d %B %Y': r'%-d %B %Y',  # 21 March 2085

            r'%b %-d %Y': r'%b %-d %Y',  # oct 12 2077

            r'%A %m/%d/%y': r'%A %m/%d/%y',  # Friday 12/09/88

            r'%-m/%-d-%y': r'%-m/%-d-%y',  # 5/23-49

        }

        for key, value in dict_patterns.items():
            if re.fullmatch(self.regex_from_date_pattern(key), input, re.IGNORECASE):
                output = self.match_case(input, self.fake_date(value))
            elif re.fullmatch(month_short_regex + key, input, re.IGNORECASE):
                output = self.match_case(input, self.fake_date_wrapper(value))
            elif re.fullmatch(month_long_regex + key, input, re.IGNORECASE):
                output = self.match_case(input, self.fake_date_wrapper(value))
            elif re.fullmatch(days_of_week_long_regex + key, input, re.IGNORECASE):
                output = self.match_case(input, self.fake_date_wrapper(value))
            elif re.fullmatch(key, input):
                output = self.fake_date_wrapper(value)


        if re.fullmatch(r'\d{4}', input):
            output = self.fake_date_wrapper('%Y')
        elif re.fullmatch(r'\d{4}-\d{4}', input):
            begin, end = input.split('-')
            offset = int(end) - int(begin)
            year = int(self.fake_date_wrapper('%Y'))
            output = str(year) + '-' + str(year + offset)
        elif re.fullmatch(month_long_regex + r'\.', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%B') + '.')
        elif re.fullmatch(month_long_regex, input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%B'))
        elif re.fullmatch(r'\d{2}-' + month_long_regex + '-\d{4}', input):
            output = self.match_case(input, self.fake_date_wrapper('%d-%b-%Y'))
        elif re.fullmatch(r'\d{,2}-' + month_long_regex + '-\d{4}', input):
            output = self.match_case(input, self.fake_date_wrapper('%-d-%b-%Y'))
        elif re.fullmatch(r'\d{2}-' + month_long_regex + '-\d{2}', input):
            output = self.match_case(input, self.fake_date_wrapper('%d-%b-%y'))
        elif re.fullmatch(r'\d{,2}-' + month_long_regex + '-\d{2}', input):
            output = self.match_case(input, self.fake_date_wrapper('%-d-%b-%y'))
        # July 23
        elif re.fullmatch(month_long_regex + ' \d{,2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%B %-d'))
        # January, 2067
        elif re.fullmatch(month_long_regex + ', \d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%B, %Y'))
        elif re.fullmatch(month_long_regex + r'\s+[12]?\d(st|nd|rd|th)', input, re.IGNORECASE):
            output = self.fake_date_wrapper('%B %-d')
            if output[-1] == '1':
                output = output + 'st'
            elif output[-1] == '2':
                output = output + 'nd'
            elif output[-1] == '3':
                output = output + 'rd'
            else:
                output = output + 'th'
        # Oct, 2079
        elif re.fullmatch(month_short_regex + r', \d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%b, %Y'))
        elif re.fullmatch(month_short_regex + r'\. \d{4}\.', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%b. %Y') + '.')
        elif re.fullmatch(month_short_regex + r'\.', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%b') + '.')
        elif re.fullmatch(month_short_regex + r',', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%b') + ',')
        elif re.fullmatch(r'\d{2}-' + month_short_regex + '-\d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%d-%b-%Y'))
        elif re.fullmatch(r'\d{,2}-' + month_short_regex + '-\d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%-d-%b-%Y'))
        # 01-Oct-82
        elif re.fullmatch(r'\d{2}-' + month_short_regex + '-\d{2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%d-%b-%y'))
        # 1-Oct-82
        elif re.fullmatch(r'\d{,2}-' + month_short_regex + '-\d{2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%-d-%b-%y'))
        # 01-Oct-2082
        elif re.fullmatch(r'\d{2}-' + month_short_regex + '-\d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%d-%b-%Y'))
        # 1-Oct-2082
        elif re.fullmatch(r'\d{,2}-' + month_short_regex + '-\d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%-d-%b-%Y'))
        # Jul 23
        elif re.fullmatch(month_short_regex + ' \d{,2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%%b %-d'))
        elif re.fullmatch(month_short_regex + r'\s+[123]?\d(st|nd|rd|th)', input, re.IGNORECASE):
            output = self.fake_date_wrapper('%b %-d')
            if output[-1] == '1':
                output = output + 'st'
            elif output[-1] == '2':
                output = output + 'nd'
            elif output[-1] == '3':
                output = output + 'rd'
            else:
                output = output + 'th'
        # 12/20/8
        elif re.fullmatch(r'\d+/\d+/\d', input):
            output = self.fake_date_wrapper('%m/%d/') + str(random.randint(0, 9))
        elif re.fullmatch(r"'\d\d", input):
            output = "'" + self.fake_date_wrapper('%y')
        # 70's
        elif re.fullmatch(r"\d\d's", input):
            output = str(random.randint(0, 9) * 10) + "'s"
        # 2070's
        elif re.fullmatch(r"\d{4}'s", input):
            output = str(random.randint(198, 209) * 10) + "'s"
        elif re.fullmatch(r'[123]?\d(st|nd|rd|th)', input, re.IGNORECASE):
            output = self.fake_date_wrapper('%-d')
            if output[-1] == '1':
                output = output + 'st'
            elif output[-1] == '2':
                output = output + 'nd'
            elif output[-1] == '3':
                output = output + 'rd'
            else:
                output = output + 'th'
        # Tuesday, November 26th
        elif re.fullmatch(days_of_week_long_regex + r', ' + month_long_regex + r' [123]?\d(st|nd|rd|th)', input,
                          re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%A, %B %-d'))
            if output[-1] == '1':
                output = output + 'st'
            elif output[-1] == '2':
                output = output + 'nd'
            elif output[-1] == '3':
                output = output + 'rd'
            else:
                output = output + 'th'

        elif re.fullmatch(days_of_week_long_regex, input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%A'))
        elif re.fullmatch(days_of_week_long_regex + r'\.', input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%A.'))
        elif re.fullmatch(days_of_week_short_regex, input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date_wrapper('%a'))
        elif re.fullmatch('|'.join(self.holidays), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_holiday())
        # M, W, F, Th, Sa
        elif re.fullmatch(days_of_week_letter_regex, input, re.IGNORECASE):
            output = self.match_case(input, random.choice(self.days_of_week_letter))
        elif re.fullmatch('|'.join(self.seasons), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_season())
        elif re.fullmatch(days_of_week_letter_regex + r'+', input, re.IGNORECASE):
            output = self.match_case(input, random.choice(['MWF', 'TuTh', 'Sat-Sun', "M-W", "W-F"]))
        elif re.fullmatch(r'(' + days_of_week_letter_regex + r', ?)+' + days_of_week_letter_regex, input,
                          re.IGNORECASE):
            output = self.match_case(input, random.choice(['M, W, F', 'Tu, Th', 'Sat, Sun', "M, W", "W, Th, F"]))

        if output.upper() == 'UNMATCHED':
            output = self.fake_date_wrapper()
        return output
