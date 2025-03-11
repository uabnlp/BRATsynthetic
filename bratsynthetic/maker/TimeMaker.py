import logging
import random
import re
from datetime import datetime, timedelta

import dateutil.parser
from dateutil.parser import parse

from .Maker import Maker

logger = logging.getLogger('BratSynthetic')


class TimeMaker(Maker):
    """
    Updated TimeMaker class that logs messages via the 'BratSynthetic' logger
    instead of printing to stdout.
    """

    def make_one(self, _input: str, no_zero_offsets=True) -> str:
        """
        Attempts to parse a time from `_input`, then generates a fake time
        within a small offset. If parsing fails, returns '[[TIME]]'.
        """
        try:
            parsed: datetime = parse(_input, fuzzy=True)
        except dateutil.parser.ParserError as e:
            logger.error(f"Error '{e}' parsing time: {_input}. Returning '[[TIME]]' as placeholder")
            return "[[TIME]]"
        except TypeError as e:
            logger.error(f"Subsequent error '{e}' (input='{_input}'). Returning '[[TIME]]' as placeholder")
            return "[[TIME]]"

        offsets: list[int] = [3, 60]  # at least 3 minutes, at least an hour

        def offset_time():
            offset: timedelta = timedelta(minutes=offsets[0])
            fake_time: datetime = self.fake.date_time_between(
                start_date=parsed - offset,
                end_date=parsed + offset
            )
            tries = 0
            # Ensure the generated time is not exactly the same as parsed
            while fake_time == parsed:
                fake_time = self.fake.date_time_between(
                    start_date=parsed - offset,
                    end_date=parsed + offset
                )
                tries += 1
                if tries > 10:
                    break
            return fake_time

        fake = offset_time()

        if no_zero_offsets:
            # If we do not allow zero-offset results, keep adjusting until different
            while fake == parsed:
                try:
                    offsets.pop(0)  # move to a larger offset
                except IndexError as e:
                    logger.error(f"Error '{e}' offsetting time: {_input}. Returning '[[TIME]]' as placeholder")
                    return "[[TIME]]"
                fake = offset_time()

        logger.debug(f"Input: '{_input}', Parsed: '{parsed}', Fake: '{fake}'")

        # Actually produce the final "synthetic" time string
        return self._make_one(_input)

    def _make_one(self, input: str) -> str:
        """
        Produces a new time string that maintains
        aspects like presence of colon, meridian, etc.
        """
        output = 'UNMATCHED'

        add_colon = ':' in input
        add_meridian = bool(re.search(r'[ap]\.?m', input, re.IGNORECASE))
        with_periods = bool(re.search(r'[ap]\.', input, re.IGNORECASE))

        if add_colon and add_meridian:
            # e.g. '1:30 AM', '12:45 p.m.'
            if with_periods:
                # e.g. 'A.M.' / 'P.M.'
                output = self.fake.time('%I:%M') + ' ' + random.choice(['A.M.', 'P.M.'])
            else:
                # e.g. 'AM' / 'PM'
                output = self.fake.time('%I:%M') + ' ' + random.choice(['AM', 'PM'])
        elif add_colon:
            # e.g. '13:45' or '01:20'
            output = self.fake.time('%H:%M')
        elif add_meridian:
            # e.g. '1am', '2 pm', '1p.m.', etc.
            if with_periods:
                output = self.fake.time('%I%M') + ' ' + random.choice(['A.M.', 'P.M.'])
            else:
                output = self.fake.time('%I%M') + ' ' + random.choice(['AM', 'PM'])
        else:
            # no colon, no AM/PM => e.g. '130', '0113', '345'
            # fallback 24hr time without colon, e.g. '1453'
            output = self.fake.time('%H%M')

        output = self.match_case(input, output)

        if output.upper() == 'UNMATCHED':
            output = self.match_case(input, self.fake.time('%H%M'))

        return output
