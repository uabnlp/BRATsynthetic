import random
import re
import os
from datetime import datetime, timedelta
import calendar

import dateutil.parser
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta as rd

from .Maker import Maker
from .. import BratSyntheticConfig
import logging

logger = logging.getLogger('BratSynthetic')


class DateMaker(Maker):
    """
    A merged DateMaker that addresses numerous edge cases:
      - Single days (like "30") that caused out-of-range errors
      - 5-digit years (like "20121") -> use first 4 digits
      - Decade notation ("1960s") -> pick random year in that decade
      - Partial numeric forms ("16/19", "19/19", "17-1") -> create a random date
      - Trailing slash ("06/29/") -> remove slash, interpret "06/29"
      - Seasons -> produce random date in that season
      - Large dictionary-based pattern matching from the original code
      - Additional fallback if everything else fails

    Incorporates further improvements:
      - Intelligent validation for two-part numeric dates (month/day vs. day/year).
      - Handling of single-integer dates with an eye to valid months for that day.
      - More robust fallback system for ambiguous or invalid numeric entries.
    """

    def __init__(self, config: BratSyntheticConfig):
        super().__init__(config)
        self.days_of_week_long = [
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'Thurday', 'satruday'
        ]
        self.days_of_week_short = [
            'mon', 'tues?', 'wen', 'wed', 'thur?', 'thr', 'thurs',
            'fri', 'sat', 'sun', 'weds'
        ]
        self.days_of_week_letter = [
            'M', 'T', 'Tu', 'W', 'Th', 'R', 'F', 'S', 'Sa',
            'Sat', 'A', 'Su'
        ]
        self.months_long = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'septemeber',
            'October', 'November', 'December', 'Decemlber'
        ]
        self.seasons = [
            'spring', 'summer', 'fall', 'winter'
        ]
        self.months_short = [
            'jan', 'feb', 'mar', 'apr', 'may', 'jun',
            'jul', 'aug', 'sept?', 'oct', 'nov', 'dec'
        ]
        self.holidays = [
            'New Year\'s', 'New Year\'s Eve', 'Memorial Day', 'Independence Day',
            'Labor Day', 'Thanksgiving', 'Christmas\\.?', 'new years',
            'New Years Eve', 'NYE', 'Ramadan'
        ]

    # ----------------------------------------------------------
    #   Utility Methods
    # ----------------------------------------------------------

    def _preprocess_input(self, raw_input: str) -> str:
        """
        - If input is strictly 5 digits, keep first 4 (e.g. '20121' -> '2012').
        - If input is a decade like '1960s', remove the trailing 's' -> '1960'.
        - Remove trailing slashes (e.g. "06/29/" -> "06/29").
        """
        processed = raw_input.strip()

        # 5-digit year => keep first 4
        if re.fullmatch(r'\d{5}', processed):
            processed = processed[:4]

        # Decade notation => remove trailing 's'
        decade_match = re.match(r'^(\d{4})s$', processed, re.IGNORECASE)
        if decade_match:
            processed = decade_match.group(1)

        # Trailing slash or multiple slashes
        processed = re.sub(r'/+$', '', processed)
        return processed

    def _validate_and_clamp_day(self, dt: datetime) -> datetime:
        """
        If the day is out of range for the month, clamp to the last valid day.
        """
        y, m, d = dt.year, dt.month, dt.day
        last_day = calendar.monthrange(y, m)[1]
        if d > last_day:
            d = last_day
        return datetime(y, m, d, dt.hour, dt.minute, dt.second,
                        dt.microsecond, dt.tzinfo)

    def _random_date_str(self, earliest_year: int = 1970) -> str:
        """
        Generate a random date (YYYY-MM-DD) in a plausible range.
        """
        year = random.randint(earliest_year, datetime.now().year + 10)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year:04d}-{month:02d}-{day:02d}"

    def _attempt_dateutil_parse(self, text: str) -> datetime or None:
        """
        Safely parse a string with dateutil, returning a datetime or None if it fails.
        """
        try:
            return parse(text, fuzzy=True)
        except (OverflowError, dateutil.parser.ParserError, TypeError, ValueError):
            return None

    def _apply_small_offset(self, dt: datetime) -> datetime:
        """
        Apply a random ±(1..3) day offset to dt, then clamp day if out of range.
        If that fails, try year offset. If that also fails, return dt unchanged.
        """
        direction = random.choice([-1, 1])
        n_units = random.randint(1, 3)
        try:
            new_dt = dt + timedelta(days=direction * n_units)
            new_dt = self._validate_and_clamp_day(new_dt)
            return new_dt
        except OverflowError:
            # fallback: shift by ±1 year
            try:
                alt = dt + rd(years=direction)
                alt = self._validate_and_clamp_day(alt)
                return alt
            except Exception:
                return dt

    # ----------------------------------------------------------
    #   Main Parsing / Wrapping
    # ----------------------------------------------------------

    def fake_date_wrapper(self, _input: str, pattern: str = "%Y-%m-%d") -> str:
        """
        Attempts to parse `_input` (after pre-processing), offset it,
        and strftime into `pattern`. Returns '[[DATE]]' on failure.
        """
        if os.name == 'nt':
            pattern = pattern.replace('%-', '%')

        processed = self._preprocess_input(_input)
        dt = self._attempt_dateutil_parse(processed)
        if dt is None:
            logger.error(f"Error parsing date: {_input}. Returning '[[DATE]]' as placeholder")
            return "[[DATE]]"

        offset_dt = self._apply_small_offset(dt)
        try:
            out = offset_dt.strftime(pattern)
        except ValueError as e:
            logger.error(f"Error '{e}' in strftime (input='{_input}'). Returning '[[DATE]]'.")
            return "[[DATE]]"

        # If out == original, try bigger offsets (month or year)
        if out == _input:
            m_dt = dt + rd(months=random.choice([-1, 1]))
            m_dt = self._validate_and_clamp_day(m_dt)
            try:
                m_out = m_dt.strftime(pattern)
            except:
                m_out = out

            if m_out != _input:
                return m_out

            y_dt = dt + rd(years=random.choice([-1, 1]))
            y_dt = self._validate_and_clamp_day(y_dt)
            try:
                y_out = y_dt.strftime(pattern)
            except:
                y_out = out

            if y_out == _input:
                logger.warning(f"Surrogate date == input. Returning '[[DATE]]'. Input='{_input}'")
                return "[[DATE]]"
            return y_out

        return out

    def regex_from_date_pattern(self, date_pattern: str) -> str:
        """
        Convert date format specifiers (e.g. %Y, %m, etc.) into regex for dictionary-based matching.
        """
        month_short_regex = '(' + '|'.join(self.months_short) + ')'
        month_long_regex = '(' + '|'.join(self.months_long) + ')'
        days_of_week_short_regex = '(' + '|'.join(self.days_of_week_short) + ')'
        days_of_week_long_regex = '(' + '|'.join(self.days_of_week_long) + ')'
        days_of_week_letter_regex = '(' + '|'.join(self.days_of_week_letter) + ')'
        seasons_regex = '(' + '|'.join(self.seasons) + ')'
        holidays_regex = '(' + '|'.join(self.holidays) + ')'

        rx = date_pattern.replace('.', r'\.')
        rx = rx.replace('%a', days_of_week_short_regex)
        rx = rx.replace('%A', days_of_week_long_regex)
        rx = rx.replace('%w', r'[0-6]')
        rx = rx.replace('%d', r'[0-3]\d')
        rx = rx.replace('%-d', r'[1-3]?\d')
        rx = rx.replace('%m', r'[0-1]\d')
        rx = rx.replace('%-m', r'[1]?\d')
        rx = rx.replace('%b', month_short_regex)
        rx = rx.replace('%B', month_long_regex)
        rx = rx.replace('%y', r'\d{2}')
        rx = rx.replace('%Y', r'\d{4}')
        rx = rx.replace('%H', r'[012]\d')
        rx = rx.replace('%-H', r'[12]?\d')
        rx = rx.replace('%I', r'[01]\d')
        rx = rx.replace('%-I', r'[1]?\d')
        rx = rx.replace('%p', r'([AP]M|[ap]m)')
        rx = rx.replace('%M', r'[0-5]\d')
        rx = rx.replace('%S', r'[0-5]\d')
        rx = rx.replace('%f', r'\d{6}')
        rx = rx.replace('%.p', r'([AP].M.|[ap].m.)')
        rx = rx.replace('%C', holidays_regex)
        rx = rx.replace('%.d', r'([0-3]\d(st|nd|rd|th))')
        rx = rx.replace('%.-d', r'([0-3]?\d(st|nd|rd|th))')
        rx = rx.replace('%>S', seasons_regex)
        return rx

    def fake_date(self, _input: str, pattern: str) -> str:
        """
        Replaces placeholders for numeric suffix and seasons, then calls `fake_date_wrapper`.
        """
        pattern = pattern.replace('%>S', random.choice(self.seasons))
        pattern = pattern.replace('%.d', '%d__NUM_SUFFIX__')
        pattern = pattern.replace('%.-d', '%-d__NUM_SUFFIX__')

        result = self.fake_date_wrapper(_input, pattern)
        if '__NUM_SUFFIX__' in result:
            idx = result.index('__NUM_SUFFIX__')
            if idx > 0:
                c = result[idx - 1]
                if c == '1':
                    suffix = 'st'
                elif c == '2':
                    suffix = 'nd'
                elif c == '3':
                    suffix = 'rd'
                else:
                    suffix = 'th'
                result = result.replace('__NUM_SUFFIX__', suffix)
            else:
                result = result.replace('__NUM_SUFFIX__', 'th')
        return result

    def fake_holiday(self) -> str:
        fake_holidays = [
            'New Year\'s', 'Memorial Day', 'Independence Day',
            'Labor Day', 'Thanksgiving', 'Christmas', 'Ramadan'
        ]
        return random.choice(fake_holidays)

    def fake_season(self) -> str:
        return random.choice(self.seasons)

    # ----------------------------------------------------------
    #   Improved Single-Integer and Two-Part Numeric Handling
    # ----------------------------------------------------------

    def _parse_single_integer_as_day(self, num_str: str) -> str:
        """
        If user typed e.g. "30", interpret as day=30 with a random month/year,
        but pick a month that can handle day=30 if possible.
        Then apply a small offset and return as YYYY-MM-DD.
        """
        day_val = int(num_str)
        if day_val < 1 or day_val > 31:
            return self._random_date_str()

        # Attempt a more "intelligent" month selection
        valid_months = []
        for m in range(1, 13):
            if day_val <= calendar.monthrange(2000, m)[1]:
                valid_months.append(m)

        if valid_months:
            month = random.choice(valid_months)
        else:
            month = random.randint(1, 12)

        year = random.randint(1970, datetime.now().year + 10)
        last_day = calendar.monthrange(year, month)[1]
        if day_val > last_day:
            day_val = last_day

        dt = datetime(year, month, day_val)
        dt = self._apply_small_offset(dt)
        return dt.strftime("%Y-%m-%d")

    def _safe_month_day(self, month: int, day: int) -> str:
        """
        Helper: Given a (month, day), pick a random year in [1970..(now+10)].
        Clamp if day out of range, apply offset.
        """
        y = random.randint(1970, datetime.now().year + 10)
        last_day = calendar.monthrange(y, month)[1]
        if day > last_day:
            day = last_day
        dt = datetime(y, month, day)
        dt = self._apply_small_offset(dt)
        return dt.strftime("%Y-%m-%d")

    def _random_month_day(self, year: int) -> str:
        """
        If we interpret the second part as a valid year, pick random (month, day).
        """
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        dt = datetime(year, month, day)
        dt = self._apply_small_offset(dt)
        return dt.strftime("%Y-%m-%d")

    def _fallback_two_part(self, d_left: int, d_right: int) -> str:
        """
        Final fallback if the two-part numeric logic fails. Just produce random date.
        Could optionally incorporate further logic.
        """
        return self._random_date_str()

    def _handle_two_part_numeric(self, left: str, right: str, sep: str) -> str:
        """
        For inputs like "16/19", "19/19", "17-1", etc.:
         - Check month/day combos in both orders
         - Check if second part is a plausible year
         - Otherwise fallback
        """
        left = left.strip()
        right = right.strip()

        if not (re.fullmatch(r'\d+', left) and re.fullmatch(r'\d+', right)):
            return self._random_date_str()

        d_left, d_right = int(left), int(right)

        # 1) Month/day
        if 1 <= d_left <= 12 and 1 <= d_right <= 31:
            return self._safe_month_day(d_left, d_right)

        # 2) Day/month
        if 1 <= d_right <= 12 and 1 <= d_left <= 31:
            return self._safe_month_day(d_right, d_left)

        # 3) If second part is a year
        if 1900 <= d_right <= 2100:
            return self._random_month_day(d_right)

        # 4) Possibly interpret second part as 2-digit year
        if len(right) == 2:
            guess_year = self._interpret_two_digit_year(d_right)
            if 1900 <= guess_year <= 2100 and 1 <= d_left <= 31:
                # treat d_left as day => pick random month
                month = random.randint(1, 12)
                last_day = calendar.monthrange(guess_year, month)[1]
                if d_left > last_day:
                    d_left = last_day
                dt = datetime(guess_year, month, d_left)
                dt = self._apply_small_offset(dt)
                return dt.strftime("%Y-%m-%d")

        # 5) Final fallback
        return self._fallback_two_part(d_left, d_right)

    def _interpret_two_digit_year(self, yy: int) -> int:
        """
        If user typed '19' => interpret as 2019 if < 40, else 19xx if >=40
        """
        if yy < 40:
            return 2000 + yy
        else:
            return 1900 + yy

    # ----------------------------------------------------------
    #   Fallback / Enhanced Parsing
    # ----------------------------------------------------------

    def _fallback_special_numeric(self, raw: str) -> str:
        """
        If raw is something like "16/19", "19/19", "17-1", "0 1/ 09" etc.
        - Remove spaces
        - Remove trailing slash or dash
        - If single integer => interpret day
        - If exactly two parts => handle via _handle_two_part_numeric
        - Else => random
        """
        txt = re.sub(r'\s+', '', raw.strip())
        txt = txt.strip('/-')

        # Single integer
        if re.fullmatch(r'\d+', txt):
            return self._parse_single_integer_as_day(txt)

        # Two parts
        if re.fullmatch(r'\d+[-/]\d+', txt):
            parts = re.split(r'[-/]', txt)
            if len(parts) == 2:
                return self._handle_two_part_numeric(parts[0], parts[1], '')
            else:
                return self._random_date_str()

        return self._random_date_str()

    def enhanced_fallback_parse(self, raw_in: str) -> str:
        """
        Our final fallback for unmatched strings. If it's numeric slash/dash => _fallback_special_numeric.
        If single day => interpret. If a known season => random date in that season. If decade => random year.
        Otherwise => random date.
        """
        text = raw_in.strip().lower()

        # Seasons
        if text in ('spring', 'summer', 'autumn', 'fall', 'winter'):
            if text == 'autumn':
                text = 'fall'
            if text == 'winter':
                possible_months = [12, 1, 2]
            elif text == 'spring':
                possible_months = [3, 4, 5]
            elif text == 'summer':
                possible_months = [6, 7, 8]
            else:
                possible_months = [9, 10, 11]
            y = random.randint(1970, datetime.now().year + 10)
            m = random.choice(possible_months)
            d = random.randint(1, 28)
            dt = datetime(y, m, d)
            dt = self._apply_small_offset(dt)
            return dt.strftime("%Y-%m-%d")

        # Decade: "1960s"
        if re.fullmatch(r'[12]\d{3}s', text):
            base_year = int(text[:-1])
            if 1900 <= base_year <= 2100:
                y = random.randint(base_year, base_year + 9)
                m = random.randint(1, 12)
                d = random.randint(1, 28)
                dt = datetime(y, m, d)
                dt = self._apply_small_offset(dt)
                return dt.strftime("%Y-%m-%d")
            else:
                return self._random_date_str()

        # If slash/dash => fallback special numeric
        if re.search(r'[-/]', text):
            return self._fallback_special_numeric(text)

        # If single day
        if re.fullmatch(r'\d{1,2}', text):
            return self._parse_single_integer_as_day(text)

        # else random
        return self._random_date_str()

    # ----------------------------------------------------------
    #   Main "make_one" method
    # ----------------------------------------------------------

    def make_one(self, _input: str) -> str:
        """
        1) Dictionary-based pattern matching from older code.
        2) Checks for year / year-range.
        3) Extended partial checks (e.g. "January.", "Feb 23rd", etc.).
        4) Final fallback parse for partial numeric or random date.
        """
        # If day-of-week with trailing 's' => remove the trailing s
        dow_plural = '|'.join(
            [d for d in self.days_of_week_long if re.match(r'^[a-zA-Z]+$', d)]
        )
        if re.fullmatch(r'(?i)(' + dow_plural + r')s', _input.strip()):
            _input = _input.strip()[:-1]

        output = 'UNMATCHED'

        # Dictionary Patterns
        month_short_regex = '(' + '|'.join(self.months_short) + ')'
        month_long_regex = '(' + '|'.join(self.months_long) + ')'
        days_of_week_short_regex = '(' + '|'.join(self.days_of_week_short) + ')'
        days_of_week_long_regex = '(' + '|'.join(self.days_of_week_long) + ')'
        days_of_week_letter_regex = '(' + '|'.join(self.days_of_week_letter) + ')'

        dict_patterns = {
            r'\s+\d{4}': '%B %Y',
            r'\s+\d{,2},\s+\d{4}': '%B %-d, %Y',
            r' 1?\d': '%B %-d',
            r' of \d{4}': '%B of %Y',
            r' \d\d\d\d': '%b %Y',
            r' 1?\d, \d{4}': '%b %-d, %Y',
            r' [0]\d, \d{2}': '%b %d, %y',
            r' [123]\d, \d{2}': '%b %-d, %y',
            r', \d{2}': '%b, %y',
            r' 0\d, \d{4}': '%b %d, %Y',
            r' \d{,2}, \d{4}': '%b %-d, %Y',
            r'\. \d{4}': '%b. %Y',
            r'': '%b',
            r'of \d{4}': '%b of %Y',
            r'(20|19|21)[0-9][0-9]': '%Y',
            r'(20|19|21)[0-9][0-9]\.': '%Y.',
            r'\d{2}': '%y',
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
            r's': '%As',
            r"%b\"": r"%b\"",
            r'%-m/%-d/%Y.': r'%-m/%-d/%Y.',
            r"%-m-%y": r"%-m-%y",
            r"%m/%d/": r"%m/%d/",
            r"%-m/ %Y": r"%-m/ %Y",
            r"%B %y": r"%B %y",
            r"%B %-d,%Y": r"%B %-d,%Y",
            r"%b%d%Y": r"%b%d%Y",
            r"%b %-d,%Y.": r"%b %-d,%Y.",
            r"%m-%d -%y": r"%m-%d -%y",
            r"%B of  %Y": r"%B of  %Y",
            r"%B of %y": r"%B of %y",
            r"%-m.%-d.%y": r"%-m.%-d.%y",
            r"%B %.-d": r"%B %.-d",
            r"%d %b %Y": r"%d %b %Y",
            r"%A %-m/%-d/%y": r"%A %-m/%-d/%y",
            r"%A, %B %-d": r"%A, %B %-d",
            r"%A %B %-d": r"%A %B %-d",
            r"%a %-m/%-d": r"%a %-m/%-d",
            r"%A, %b %d, %Y": r"%A, %b %d, %Y",
            r"%A, %B %d, %Y": r"%A, %B %d, %Y",
            r"%b/%y": r"%b/%y",
            r"%b%d": r"%b%d",
            r"%b-%Y": r"%b-%Y",
            r"%B. %Y": r"%B. %Y",
            r"%b. %d, %Y": r"%b. %d, %Y",
            r"%>S, %Y": r"%>S, %Y",
            r"%.-d of %B": r"%.-d of %B",
            r"the %.-d": r"the %.-d",
            r" % B % y": r" % B % y",
            r"%-m/%-d,%y": r"%-m/%-d,%y",
            r"%-m-%-d": r"%-m-%-d",
            r"%d/%m": r"%d/%m",
            r"%B %d %Y": r"%B %d %Y",
            r"%b. %d": r"%b. %d",
            r"%d %B %y": r"%d %B %y",
            r"%d %b %y": r"%d %b %y",
            r"%>S %Y": r"%>S %Y",
            r"%>S of %Y": r"%>S of %Y",
            r"%>S of %y": r"%>S of %y",
            r"Fall %m/%d": r"Fall %m/%d",
            r"%B ‘%y": r"%B ‘%y",
            r"%b ‘%y": r"%b ‘%y",
            r"%b. ‘%y": r"%b. ‘%y",
            r"%-m/'%y": r"%-m/'%y",
            r'%m\.%d\.%y': r'%m.%d.%y',
            r'%B %.d, %Y': r'%B %.d, %Y',
            r'%B %.-d, %Y': r'%B %.-d, %Y',
            r'%b %.-d %Y': r'%b %.-d %Y',
            r'%d%b%y': r'%d%b%y',
            r'%b. %-d': r'%b. %-d',
            r'%b %-d\.': r'%b %-d.',
            r'%B %-d\.': r'%B %-d.',
            r'%A, %B %-d, %Y': r'%A, %B %-d, %Y',
            r'%d %B %Y': r'%d %B %Y',
            r'%-d %B %Y': r'%-d %B %Y',
            r'%b %-d %Y': r'%b %-d %Y',
            r'%A %m/%d/%y': r'%A %m/%d/%y',
            r'%-m/%-d-%y': r'%-m/%-d-%y',
        }

        # Try dictionary-based approach
        for key, val in dict_patterns.items():
            pat_rx = self.regex_from_date_pattern(key)
            if re.fullmatch(pat_rx, _input, re.IGNORECASE):
                output = self.match_case(_input, self.fake_date(_input, pattern=val))
            elif re.fullmatch(month_short_regex + key, _input, re.IGNORECASE):
                output = self.match_case(_input, self.fake_date_wrapper(_input, pattern=val))
            elif re.fullmatch(month_long_regex + key, _input, re.IGNORECASE):
                output = self.match_case(_input, self.fake_date_wrapper(_input, pattern=val))
            elif re.fullmatch(days_of_week_long_regex + key, _input, re.IGNORECASE):
                output = self.match_case(_input, self.fake_date_wrapper(_input, pattern=val))
            elif re.fullmatch(key, _input):
                output = self.fake_date_wrapper(_input, pattern=val)

            if output != 'UNMATCHED':
                break

        # Check for 4-digit year or year-range if still unmatched
        if output == 'UNMATCHED':
            if re.fullmatch(r'\d{4}', _input):
                output = self.fake_date_wrapper(_input, pattern='%Y')
            elif re.fullmatch(r'\d{4}-\d{4}', _input):
                b, e = _input.split('-')
                if b == e:
                    output = _input
                else:
                    try:
                        offset = int(e) - int(b)
                        year_str = self.fake_date_wrapper(b, pattern='%Y')
                        if year_str.isdigit():
                            base_year = int(year_str)
                            output = f"{base_year}-{base_year + offset}"
                        else:
                            output = _input
                    except:
                        output = _input

        # Extended partial checks
        if output == 'UNMATCHED':
            output = self._extended_partial_checks(_input)

        # Final fallback
        if output.upper() == 'UNMATCHED':
            fallback_date_str = self.enhanced_fallback_parse(_input)
            if fallback_date_str == "[[DATE]]":
                output = "[[DATE]]"
            else:
                output = self.fake_date_wrapper(fallback_date_str)

        return output

    def _extended_partial_checks(self, _input: str) -> str:
        """
        Additional partial checks for strings not found by dictionary patterns.
        Returns 'UNMATCHED' if not recognized.
        """
        output = 'UNMATCHED'
        ml_regex = '(' + '|'.join(self.months_long) + ')'
        ms_regex = '(' + '|'.join(self.months_short) + ')'
        dwl_regex = '(' + '|'.join(self.days_of_week_long) + ')'
        dws_regex = '(' + '|'.join(self.days_of_week_short) + ')'
        dwlet_regex = '(' + '|'.join(self.days_of_week_letter) + ')'

        # e.g. "January."
        if re.fullmatch(ml_regex + r'\.', _input, re.IGNORECASE):
            new_base = _input[:-1]
            replaced = self.fake_date_wrapper(new_base, pattern='%B')
            output = self.match_case(_input, replaced + '.')

        # e.g. "January"
        elif re.fullmatch(ml_regex, _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%B')
            output = self.match_case(_input, replaced)

        # e.g. "01-January-2020"
        elif re.fullmatch(r'\d{2}-' + ml_regex + r'-\d{4}', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%d-%b-%Y')
            output = self.match_case(_input, replaced)
        elif re.fullmatch(r'\d{,2}-' + ml_regex + r'-\d{4}', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%-d-%b-%Y')
            output = self.match_case(_input, replaced)
        elif re.fullmatch(r'\d{2}-' + ml_regex + r'-\d{2}', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%d-%b-%y')
            output = self.match_case(_input, replaced)
        elif re.fullmatch(r'\d{,2}-' + ml_regex + r'-\d{2}', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%-d-%b-%y')
            output = self.match_case(_input, replaced)

        # e.g. "January 23"
        elif re.fullmatch(ml_regex + r' \d{1,2}', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%B %-d')
            output = self.match_case(_input, replaced)

        # e.g. "January, 2020"
        elif re.fullmatch(ml_regex + r', \d{4}', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%B, %Y')
            output = self.match_case(_input, replaced)

        # e.g. "January 23rd"
        elif re.fullmatch(ml_regex + r'\s+[123]?\d(st|nd|rd|th)', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%B %-d')
            if replaced and replaced[-1].isdigit():
                if replaced[-1] == '1':
                    replaced += 'st'
                elif replaced[-1] == '2':
                    replaced += 'nd'
                elif replaced[-1] == '3':
                    replaced += 'rd'
                else:
                    replaced += 'th'
            output = replaced

        # e.g. "Feb."
        elif re.fullmatch(ms_regex + r'\.', _input, re.IGNORECASE):
            new_base = _input[:-1]
            replaced = self.fake_date_wrapper(new_base, pattern='%b')
            output = self.match_case(_input, replaced + '.')

        # e.g. "Feb,"
        elif re.fullmatch(ms_regex + r',', _input, re.IGNORECASE):
            new_base = _input[:-1]
            replaced = self.fake_date_wrapper(new_base, pattern='%b')
            output = self.match_case(_input, replaced + ',')

        # e.g. "11-Feb-2020"
        elif re.fullmatch(r'\d{2}-' + ms_regex + r'-\d{4}', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%d-%b-%Y')
            output = self.match_case(_input, replaced)
        elif re.fullmatch(r'\d{,2}-' + ms_regex + r'-\d{4}', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%-d-%b-%Y')
            output = self.match_case(_input, replaced)
        elif re.fullmatch(r'\d{2}-' + ms_regex + r'-\d{2}', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%d-%b-%y')
            output = self.match_case(_input, replaced)
        elif re.fullmatch(r'\d{,2}-' + ms_regex + r'-\d{2}', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%-d-%b-%y')
            output = self.match_case(_input, replaced)

        # e.g. "Feb 23"
        elif re.fullmatch(ms_regex + r' \d{1,2}', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%b %-d')
            output = self.match_case(_input, replaced)

        # e.g. "Feb 23rd"
        elif re.fullmatch(ms_regex + r'\s+[123]?\d(st|nd|rd|th)', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%b %-d')
            if replaced and replaced[-1].isdigit():
                if replaced[-1] == '1':
                    replaced += 'st'
                elif replaced[-1] == '2':
                    replaced += 'nd'
                elif replaced[-1] == '3':
                    replaced += 'rd'
                else:
                    replaced += 'th'
            output = replaced

        # e.g. "12/20/8"
        elif re.fullmatch(r'\d+/\d+/\d', _input):
            partial = self.fake_date_wrapper(_input, pattern='%m/%d/')
            if partial != "[[DATE]]":
                partial += str(random.randint(0, 9))
            output = partial

        # e.g. "'70"
        elif re.fullmatch(r"'\d\d", _input):
            replaced = self.fake_date_wrapper(_input, pattern='%y')
            if replaced == "[[DATE]]":
                output = "[[DATE]]"
            else:
                output = "'" + replaced

        # e.g. "70's"
        elif re.fullmatch(r"\d\d's", _input):
            decade = random.randint(0, 9) * 10
            output = f"{decade}'s"

        # e.g. "1970's"
        elif re.fullmatch(r"\d{4}'s", _input):
            base = random.randint(198, 209) * 10
            output = f"{base}'s"

        # e.g. "31st"
        elif re.fullmatch(r'[123]?\d(st|nd|rd|th)', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%-d')
            if replaced and replaced[-1].isdigit():
                if replaced[-1] == '1':
                    replaced += 'st'
                elif replaced[-1] == '2':
                    replaced += 'nd'
                elif replaced[-1] == '3':
                    replaced += 'rd'
                else:
                    replaced += 'th'
            output = replaced

        # e.g. "Tuesday, November 26th"
        elif re.fullmatch(dwl_regex + r', ' + ml_regex + r' [123]?\d(st|nd|rd|th)', _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%A, %B %-d')
            if replaced and replaced[-1].isdigit():
                if replaced[-1] == '1':
                    replaced += 'st'
                elif replaced[-1] == '2':
                    replaced += 'nd'
                elif replaced[-1] == '3':
                    replaced += 'rd'
                else:
                    replaced += 'th'
            output = replaced

        # e.g. "Tuesday" or "Tuesday."
        elif re.fullmatch(dwl_regex, _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%A')
            output = self.match_case(_input, replaced)
        elif re.fullmatch(dwl_regex + r'\.', _input, re.IGNORECASE):
            stripped = _input[:-1]
            replaced = self.fake_date_wrapper(stripped, pattern='%A')
            output = self.match_case(_input, replaced + '.')

        # e.g. "wed"
        elif re.fullmatch(dws_regex, _input, re.IGNORECASE):
            replaced = self.fake_date_wrapper(_input, pattern='%a')
            output = self.match_case(_input, replaced)

        # e.g. "New Year's"
        elif re.fullmatch('|'.join(self.holidays), _input, re.IGNORECASE):
            replaced = self.fake_holiday()
            output = self.match_case(_input, replaced)

        # e.g. "M", "Tu"
        elif re.fullmatch(dwlet_regex, _input, re.IGNORECASE):
            output = self.match_case(_input, random.choice(self.days_of_week_letter))

        # e.g. "MWF", "TTT"
        elif re.fullmatch(dwlet_regex + r'+', _input, re.IGNORECASE):
            output = self.match_case(_input, random.choice(['MWF', 'TuTh', 'Sat-Sun', 'M-W', 'W-F']))

        # e.g. "M, W, F"
        elif re.fullmatch(r'(' + dwlet_regex + r',?\s?)+' + dwlet_regex, _input, re.IGNORECASE):
            output = self.match_case(_input, random.choice(['M, W, F', 'Tu, Th', 'Sat, Sun', 'M, W', 'W, Th, F']))

        return output
