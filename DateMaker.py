from .Maker import Maker
import random
import re

class DateMaker(Maker):

    def __init__(self):
        super().__init__()
        self.days_of_week_long = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'Thurday']
        self.days_of_week_short = ['mon', 'tues?', 'wen', 'wed', 'thur?', 'thr', 'thurs', 'fri', 'sat', 'sun']
        self.months_long = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                            'October', 'November', 'December']

        self.seasons = ['spring', 'summer', 'fall', 'winter']
        self.months_short = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept?', 'oct', 'nov', 'dec']
        self.holidays = ['New Year\'s', 'Memorial Day', 'Independence Day', 'Labor Day', 'Thanksgiving', 'Christmas\.?', 'new years', 'New Years Eve', 'NYE']


    def fake_holiday(self):
        fake_holidays = ['New Year\'s', 'Memorial Day', 'Independence Day', 'Labor Day', 'Thanksgiving', 'Christmas']
        return random.choice(fake_holidays)

    def fake_season(self):
        return random.choice(self.seasons)

    def make(self, input: str) -> str:
        output = 'UNMATCHED'

        month_short_regex = '(' + '|'.join(self.months_short) + ')'
        month_long_regex = '(' + '|'.join(self.months_long) + ')'
        days_of_week_short_regex = '(' + '|'.join(self.days_of_week_short) + ')'
        days_of_week_long_regex = '(' + '|'.join(self.days_of_week_long) + ')'

        if re.fullmatch(r'(20|19)[0-2][0-9]', input):
            output = self.fake.date('%Y')
        if re.fullmatch(r'(20|19)[0-2][0-9].', input):
            output = self.fake.date('%Y.')
        elif re.fullmatch(r'\d\d\d\d', input):
            output = self.fake.date('%H%M')
        elif re.fullmatch(r'\d{4}-\d{4}', input):
            begin, end = input.split('-')
            offset = int(end) - int(begin)
            year = int(self.fake.date('%Y'))
            output = str(year) + '-' + str(year+offset)

        elif re.fullmatch(month_long_regex + r'\s+\d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B %Y'))
        elif re.fullmatch(month_long_regex + r'\s+1?\d,\s+\d{4}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B %-d, %Y'))
        elif re.fullmatch(month_long_regex + r'\s+1?\d,\s+\d{2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B -d, %y'))
        elif re.fullmatch(month_long_regex + r' 1?\d', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B %-d'))
        elif re.fullmatch(month_long_regex + r'\.', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B') + '.')
        elif re.fullmatch(month_long_regex, input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%B'))
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
        elif re.fullmatch(month_short_regex + r' 1?\d, \d{2}', input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%b %-d, %y'))
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

        elif re.fullmatch(r'1?\d-1?\d$', input):
            output = self.fake.date('%m-%-d')
        elif re.fullmatch(r'[01]\d-[0123]\d$', input):
            output = self.fake.date('%m-%d')
        elif re.fullmatch(r'\d+/\d+/\d{2}$', input):
            output = self.fake.date('%m/%d/%y')
        elif re.fullmatch(r'\d+/\d+/\d{4}', input):
            output = self.fake.date('%m/%d/%Y')
        elif re.fullmatch(r'\d+-\d+-\d{4}', input):
            output = self.fake.date('%m-%d-%Y')
        elif re.fullmatch(r"'\d\d", input):
            output = "'" + self.fake.date('%y')
        elif re.fullmatch(r'[01]?\d/\d{1,2}$', input):
            output = self.fake.date('%m/%d')
        elif re.fullmatch(r'[01]?\d/\d{4}', input):
            output = self.fake.date('%m/%Y')
        elif re.fullmatch(r'[12]?\d(st|nd|rd|th)', input, re.IGNORECASE):
            output = self.fake.date('%d').strip('0')
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
        elif re.fullmatch(days_of_week_short_regex, input, re.IGNORECASE):
            output = self.match_case(input, self.fake.date('%a'))
        elif re.fullmatch('|'.join(self.holidays), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_holiday())

        elif re.fullmatch('|'.join(self.seasons), input, re.IGNORECASE):
            output = self.match_case(input, self.fake_season())

        # print(f'DateMaker: {input} -> {output}')
        if output.upper() == 'UNMATCHED':
          output = self.fake.date('%m/%d/%Y') # Default date if no regex matched.
        return output
