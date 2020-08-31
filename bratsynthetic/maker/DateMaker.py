from .Maker import Maker
import random
import re

class DateMaker(Maker):

    def __init__(self):
        super().__init__()
        self.days_of_week_long = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'Thurday']
        self.days_of_week_short = ['mon', 'tues?', 'wen', 'wed', 'thur?', 'thr', 'thurs', 'fri', 'sat', 'sun']
        self.days_of_week_letter = ['M', 'T', 'Tu', 'W', 'Th', 'R', 'F', 'S', 'Sa', 'A', 'Su']
        self.months_long = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                            'October', 'November', 'December']

        self.seasons = ['spring', 'summer', 'fall', 'winter']
        self.months_short = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept?', 'oct', 'nov', 'dec']

        self.holidays = ['New Year\'s', 'New Year\'s Eve', 'Memorial Day', 'Independence Day', 'Labor Day', 'Thanksgiving', 'Christmas\.?', 'new years', 'New Years Eve', 'NYE', 'Ramadan']


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
        regex = regex.replace('%.p', r'([AP].M.|[ap].m.')  #Looks for period
        regex = regex.replace('%C', holidays_regex) #Look for Holidays
        regex = regex.replace('%.d', r'[0-3]\d(st|nd|rd|th)')
        regex = regex.replace('%.-d', r'[1-3]?\d(st|nd|rd|th)')
        regex = regex.replace('%>S', seasons_regex)

        return regex

    def fake_date(self, pattern: str) -> str:

        pattern = pattern.replace('%.d', '%d__NUM_SUFFIX__')
        pattern = pattern.replace('%.-d', '%-d__NUM_SUFFIX__')
        pattern = pattern.replace('%>S', random.choice(self.seasons))

        output = self.fake.date(pattern)

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
        fake_holidays = ['New Year\'s', 'Memorial Day', 'Independence Day', 'Labor Day', 'Thanksgiving', 'Christmas', 'Ramadan']
        return random.choice(fake_holidays)

    def fake_season(self):
        return random.choice(self.seasons)

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        month_short_regex = '(' + '|'.join(self.months_short) + ')'
        month_long_regex = '(' + '|'.join(self.months_long) + ')'
        days_of_week_short_regex = '(' + '|'.join(self.days_of_week_short) + ')'
        days_of_week_long_regex = '(' + '|'.join(self.days_of_week_long) + ')'
        days_of_week_letter_regex = '(' + '|'.join(self.days_of_week_letter) + ')'

        if re.fullmatch(r'(20|19|21)[0-9][0-9]', input):
            output = self.fake.date('%Y')
        elif re.fullmatch(r'(20|19|21)[0-9][0-9].', input):
            output = self.fake.date('%Y.')
        # 06
        elif re.fullmatch(r'\d{2}', input):
            output = self.fake.date('%y')
        elif re.fullmatch(r'\d{4}-\d{4}', input):
            begin, end = input.split('-')
            offset = int(end) - int(begin)
            year = int(self.fake.date('%Y'))
            output = str(year) + '-' + str(year+offset)
        # 11-70
        elif re.fullmatch(self.regex_from_date_pattern(r"%-m-%y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%-m-%y"))
        # 07/28/
        elif re.fullmatch(self.regex_from_date_pattern(r"%m/%d/"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%m/%d/"))
        # 4/ 2064
        elif re.fullmatch(self.regex_from_date_pattern(r"%-m/ %Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%-m/ %Y"))
        # July O2
        elif re.fullmatch(self.regex_from_date_pattern(r"%B %y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%B %y"))
        # March 25,2064
        elif re.fullmatch(self.regex_from_date_pattern(r"%B %-d,%Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%B %-d,%Y"))
        # 12-21 -97
        elif re.fullmatch(self.regex_from_date_pattern(r"%m-%d -%y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%m-%d -%y"))
        # April of  2096
        elif re.fullmatch(self.regex_from_date_pattern(r"%B of  %Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%B of  %Y"))
        # November of 73
        elif re.fullmatch(self.regex_from_date_pattern(r"%B of %y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%B of %y"))
        # 3.23.64
        elif re.fullmatch(self.regex_from_date_pattern(r"%-m.%-d.%y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%-m.%-d.%y"))
        # August 30th
        elif re.fullmatch(self.regex_from_date_pattern(r"%B %.-d"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%B %.-d"))
        # 07 Apr 2113
        elif re.fullmatch(self.regex_from_date_pattern(r"%d %b %Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%d %b %Y"))
        # Saturday 7/28/91
        elif re.fullmatch(self.regex_from_date_pattern(r"%A %-m/%-d/%y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%A %-m/%-d/%y"))
        # Friday, June 19
        elif re.fullmatch(self.regex_from_date_pattern(r"%A, %B %-d"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%A, %B %-d"))
        # Wednesday June 21
        elif re.fullmatch(self.regex_from_date_pattern(r"%A %B %-d"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%A %B %-d"))
        # Tuesday, Apr 27, 2073
        elif re.fullmatch(self.regex_from_date_pattern(r"%A, %b %d, %Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%A, %b %d, %Y"))
        # Tuesday, October 01, 2074
        elif re.fullmatch(self.regex_from_date_pattern(r"%A, %B %d, %Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%A, %B %d, %Y"))
        # aug/82
        elif re.fullmatch(self.regex_from_date_pattern(r"%b/%y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%b/%y"))
        # jan30
        elif re.fullmatch(self.regex_from_date_pattern(r"%b%d"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%b%d"))
        # Nov-2078
        elif re.fullmatch(self.regex_from_date_pattern(r"%b-%Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%b-%Y"))
        # September. 2092
        elif re.fullmatch(self.regex_from_date_pattern(r"%B. %Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%B. %Y"))
        # Jan. 24, 2094
        elif re.fullmatch(self.regex_from_date_pattern(r"%b. %d, %Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%b. %d, %Y"))
        # spring, 2081
        elif re.fullmatch(self.regex_from_date_pattern(r"%>S, %Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%>S, %Y"))
        # 12th of September
        elif re.fullmatch(self.regex_from_date_pattern(r"%.-d of %B"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%.-d of %B"))
        # june77
        elif re.fullmatch(self.regex_from_date_pattern(r"%B%y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%B%y"))
        # 1/10,77
        elif re.fullmatch(self.regex_from_date_pattern(r"%-m/%-d,%y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%-m/%-d,%y"))
        # 1-24
        elif re.fullmatch(self.regex_from_date_pattern(r"%-m-%-d"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%-m-%-d"))
        # 21/05
        elif re.fullmatch(self.regex_from_date_pattern(r"%d/%m"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%d/%m"))
        # September 24 2132
        elif re.fullmatch(self.regex_from_date_pattern(r"%B %d %Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%B %d %Y"))
        # Feb. 02
        elif re.fullmatch(self.regex_from_date_pattern(r"%b. %d"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%b. %d"))
        # 31 August 41
        elif re.fullmatch(self.regex_from_date_pattern(r"%d %B %y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%d %B %y"))
        # 26 Jun 92
        elif re.fullmatch(self.regex_from_date_pattern(r"%d %b %y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%d %b %y"))
        # spring 2090
        elif re.fullmatch(self.regex_from_date_pattern(r"%>S %Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%>S %Y"))
        # spring of 2094
        elif re.fullmatch(self.regex_from_date_pattern(r"%>S of %Y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%>S of %Y"))
        # Fall of 77
        elif re.fullmatch(self.regex_from_date_pattern(r"%>S of %y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%>S of %y"))
        # March '72
        elif re.fullmatch(self.regex_from_date_pattern(r"%B '%y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%B '%y"))
        # Oct '64
        elif re.fullmatch(self.regex_from_date_pattern(r"%b '%y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%b '%y"))
        # Oct. '94
        elif re.fullmatch(self.regex_from_date_pattern(r"%b. '%y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%b. '%y"))
        # 2/'95
        elif re.fullmatch(self.regex_from_date_pattern(r"%-m/'%y"), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r"%-m/'%y"))
        # 04.15.94
        elif re.fullmatch(self.regex_from_date_pattern(r'%m.%d.%y'), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r'%m.%d.%y'))
        # May 09th, 2092
        elif re.fullmatch(self.regex_from_date_pattern(r'%B %.d, %Y'), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r'%B %.d, %Y'))
        # May 9th, 2092
        elif re.fullmatch(self.regex_from_date_pattern(r'%B %.-d, %Y'), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_date(r'%B %.-d, %Y'))
        # 30Aug71
        elif re.fullmatch(self.regex_from_date_pattern(r'%d%b%y'), input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date(r'%d%b%y'))
        # Nov. 10
        elif re.fullmatch(self.regex_from_date_pattern(r'%b. %-d'), input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date(r'%b. %-d'))
        # Thursday, February 20, 2089
        elif re.fullmatch(self.regex_from_date_pattern(r'%A, %B %-d, %Y'), input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date(r'%A, %B %-d, %Y'))
        # 09 September 2083
        elif re.fullmatch(self.regex_from_date_pattern(r'%d %B %Y'), input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date(r'%d %B %Y'))
        # 21 March 2085
        elif re.fullmatch(self.regex_from_date_pattern(r'%-d %B %Y'), input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date(r'%-d %B %Y'))
        # oct 12 2077
        elif re.fullmatch(self.regex_from_date_pattern(r'%b %-d %Y'), input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date(r'%b %-d %Y'))
        # Friday 12/09/88
        elif re.fullmatch(self.regex_from_date_pattern(r'%A %m/%d/%y'), input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date(r'%A %m/%d/%y'))
        # 5/23-49
        elif re.fullmatch(self.regex_from_date_pattern(r'%-m/%-d-%y'), input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date(r'%-m/%-d-%y'))
        elif re.fullmatch(month_long_regex + r'\s+\d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B %Y'))
        elif re.fullmatch(month_long_regex + r'\s+\d{,2},\s+\d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B %-d, %Y'))
        elif re.fullmatch(month_long_regex + r' 1?\d', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B %-d'))
        elif re.fullmatch(month_long_regex + r'\.', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B') + '.')
        elif re.fullmatch(month_long_regex, input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B'))
        # September of 2080
        elif re.fullmatch(month_long_regex + r' of \d{4}', input):
            output = self.match_case(input, self.fake.date('%B of %Y'))
        elif re.fullmatch(r'\d{2}-' + month_long_regex + '-\d{4}', input):
            output = self.match_case(input, self.fake.date('%d-%b-%Y'))
        elif re.fullmatch(r'\d{,2}-' + month_long_regex + '-\d{4}', input):
            output = self.match_case(input, self.fake.date('%-d-%b-%Y'))
        elif re.fullmatch(r'\d{2}-' + month_long_regex + '-\d{2}', input):
            output = self.match_case(input, self.fake.date('%d-%b-%y'))
        elif re.fullmatch(r'\d{,2}-' + month_long_regex + '-\d{2}', input):
            output = self.match_case(input, self.fake.date('%-d-%b-%y'))
        # July 23
        elif re.fullmatch(month_long_regex + ' \d{,2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B %-d'))
        # January, 2067
        elif re.fullmatch(month_long_regex + ', \d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B, %Y'))
        elif re.fullmatch(month_long_regex + r'\s+[12]?\d(st|nd|rd|th)', input, re.IGNORECASE):
            output = self.fake.date('%B %-d')
            if output[-1] == '1':
                output = output + 'st'
            elif output[-1] == '2':
                output = output + 'nd'
            elif output[-1] == '3':
                output = output + 'rd'
            else:
                output = output + 'th'

        elif re.fullmatch(month_short_regex + r' \d\d\d\d', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b %Y'))
        elif re.fullmatch(month_short_regex + r' 1?\d', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b %-d'))
        elif re.fullmatch(month_short_regex + r' 1?\d, \d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b %-d, %Y'))
        elif re.fullmatch(month_short_regex + r' [0]\d, \d{2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b %d, %y'))
        elif re.fullmatch(month_short_regex + r' [123]\d, \d{2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b %-d, %y'))
        # Oct, 2079
        elif re.fullmatch(month_short_regex + r', \d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b, %Y'))
        # Oct, 79
        elif re.fullmatch(month_short_regex + r', \d{2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b, %y'))
        # Mar 09, 2067
        elif re.fullmatch(month_short_regex + r' 0\d, \d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b %d, %Y'))
        elif re.fullmatch(month_short_regex + r' \d{,2}, \d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b %-d, %Y'))
        elif re.fullmatch(month_short_regex + r'\. \d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b. %Y'))
        elif re.fullmatch(month_short_regex + r'\. \d{4}\.', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b. %Y') + '.')
        elif re.fullmatch(month_short_regex + r'\.', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b') + '.')
        elif re.fullmatch(month_short_regex + r'', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b'))
        elif re.fullmatch(month_short_regex + r',', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b') + ',')
        # Sept of 2080
        elif re.fullmatch(month_short_regex + r'of \d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b of %Y'))
        elif re.fullmatch(r'\d{2}-' + month_short_regex + '-\d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%d-%b-%Y'))
        elif re.fullmatch(r'\d{,2}-' + month_short_regex + '-\d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%-d-%b-%Y'))
        # 01-Oct-82
        elif re.fullmatch(r'\d{2}-' + month_short_regex + '-\d{2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%d-%b-%y'))
        # 1-Oct-82
        elif re.fullmatch(r'\d{,2}-' + month_short_regex + '-\d{2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%-d-%b-%y'))
        # 01-Oct-2082
        elif re.fullmatch(r'\d{2}-' + month_short_regex + '-\d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%d-%b-%Y'))
        # 1-Oct-2082
        elif re.fullmatch(r'\d{,2}-' + month_short_regex + '-\d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%-d-%b-%Y'))
        # Jul 23
        elif re.fullmatch(month_short_regex + ' \d{,2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%%b %-d'))
        elif re.fullmatch(month_short_regex + r'\s+[123]?\d(st|nd|rd|th)', input, re.IGNORECASE):
            output = self.fake.date('%b %-d')
            if output[-1] == '1':
                output = output + 'st'
            elif output[-1] == '2':
                output = output + 'nd'
            elif output[-1] == '3':
                output = output + 'rd'
            else:
                output = output + 'th'

        elif re.fullmatch(r'\d{4}-\d{2}-\d{2}', input):
            output = self.fake.date('%Y-%m-%d')
        elif re.fullmatch(r'\d{2}-\d{2}-\d{2}', input):
            output = self.fake.date('%m-%d-%y')
        elif re.fullmatch(r'\d{,2}-\d{,2}-\d{2}', input):
            output = self.fake.date('%-m-%-d-%y')
        elif re.fullmatch(r'1?\d-1?\d$', input):
            output = self.fake.date('%m-%-d')
        elif re.fullmatch(r'\d\d?/ \d{2}', input):
            output = self.fake.date('%-m/ %y')
        elif re.fullmatch(r'[01]\d-[0123]\d$', input):
            output = self.fake.date('%m-%d')
        elif re.fullmatch(r'\d+/\d+/\d{2}$', input):
            output = self.fake.date('%m/%d/%y')
        elif re.fullmatch(r'\d+/\d+/\d{4}', input):
            output = self.fake.date('%m/%d/%Y')
        # 12/20/8
        elif re.fullmatch(r'\d+/\d+/\d', input):
            output = self.fake.date('%m/%d/') + str(random.randint(0, 9))
        elif re.fullmatch(r'\d+-\d+-\d{4}', input):
            output = self.fake.date('%m-%d-%Y')
        elif re.fullmatch(r"'\d\d", input):
            output = "'" + self.fake.date('%y')
        elif re.fullmatch(r'[01]?\d/\d{1,2}$', input):
            output = self.fake.date('%m/%d')
        elif re.fullmatch(r'[01]?\d/\d{4}', input):
            output = self.fake.date('%m/%Y')
        # 70's
        elif re.fullmatch(r"\d\d's", input):
            output = str(random.randint(0, 9) * 10) + "'s"
        # 2070's
        elif re.fullmatch(r"\d{4}'s", input):
            output = str(random.randint(198, 209) * 10) + "'s"
        elif re.fullmatch(r'[123]?\d(st|nd|rd|th)', input, re.IGNORECASE):
            output = self.fake.date('%-d')
            if output[-1] == '1':
                output = output + 'st'
            elif output[-1] == '2':
                output = output + 'nd'
            elif output[-1] == '3':
                output = output + 'rd'
            else:
                output = output + 'th'
        # Tuesday, November 26th
        elif re.fullmatch(days_of_week_long_regex + r', ' + month_long_regex + r' [123]?\d(st|nd|rd|th)', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%A, %B %-d'))
            if output[-1] == '1':
                output = output + 'st'
            elif output[-1] == '2':
                output = output + 'nd'
            elif output[-1] == '3':
                output = output + 'rd'
            else:
                output = output + 'th'

        elif re.fullmatch(days_of_week_long_regex, input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%A'))
        elif re.fullmatch(days_of_week_long_regex + r'\.', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%A.'))
        # Thursdays
        elif re.fullmatch(days_of_week_long_regex + r's', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%As'))
        elif re.fullmatch(days_of_week_short_regex, input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%a'))
        elif re.fullmatch('|'.join(self.holidays), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_holiday())
        # M, W, F, Th, Sa
        elif re.fullmatch(days_of_week_letter_regex, input, re.IGNORECASE):
            output = self.match_case(input, random.choice(self.days_of_week_letter))
        elif re.fullmatch('|'.join(self.seasons), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_season())

        # print(f'DateMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
            output = self.fake.date()
        return output
