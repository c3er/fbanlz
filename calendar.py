"""Calendar printing functions

Based on the module with same name of the official Python 3.6 distribution.

Note when comparing these calendars to the ones printed by cal(1): By
default, these calendars have Monday as the first day of the week, and
Sunday as the last (the European convention). Use setfirstweekday() to
set the first day of the week (0=Monday, 6=Sunday).
"""


import sys
import datetime
import locale as _locale
from itertools import repeat


# Constants for months referenced later
JANUARY = 1
FEBRUARY = 2

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
    <head>
        <title>Facebook logon overview</title>
        <meta charset="utf-8" />
        <style type="text/css">
            table {
                margin: 10px;
                border-collapse: collapse;
                border-spacing: 0;
            }
            table.month {
                border: 1px solid #707070;
            }
            td {
                padding: 10px;
                vertical-align: top;
            }
            .day {
                border: 1px solid #707070;
            }
        </style>
        <style type="text/css">
            {{STYLE}}
        </style>
    </head>
    <body>
        {{CONTENT}}
    </body>
</html>
"""


# Number of days per month (except for February in leap years)
mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

day_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
month_name = [
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

# Constants for weekdays
(MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY) = range(7)


# Exceptions raised for bad input
class IllegalMonthError(ValueError):
    def __init__(self, month):
        self.month = month
    def __str__(self):
        return f"bad month number {self.month}; must be between 1 and 12"


def isleap(year):
    """Return True for leap years, False for non-leap years."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def leapdays(year1, year2):
    """Return number of leap years in range [year1, year2).
    Assume year1 <= year2.
    """
    year1 -= 1
    year2 -= 1
    return (year2 // 4 - year1 // 4) - (year2 // 100 - year1 // 100) + (year2 // 400 - year1 // 400)


def weekday(year, month, day):
    """Return weekday (0-6 ~ Mon-Sun) for year (1970-...), month (1-12),
       day (1-31).
    """
    return datetime.date(year, month, day).weekday()


def monthrange(year, month):
    """Return weekday (0-6 ~ Mon-Sun) and number of days (28-31) for
       year, month.
    """
    if not 1 <= month <= 12:
        raise IllegalMonthError(month)
    day1 = weekday(year, month, 1)
    ndays = mdays[month] + (month == FEBRUARY and isleap(year))
    return day1, ndays


class Calendar(object):
    """Base calendar class. This class doesn't do any formatting. It simply
    provides data to subclasses.
    """
    def __init__(self, firstweekday=0):
        self.firstweekday = firstweekday  # 0 = Monday, 6 = Sunday

    def getfirstweekday(self):
        return self._firstweekday % 7

    def setfirstweekday(self, firstweekday):
        self._firstweekday = firstweekday

    firstweekday = property(getfirstweekday, setfirstweekday)

    def iterweekdays(self):
        """Return an iterator for one week of weekday numbers starting with the
        configured first one.
        """
        for weekdays in range(self.firstweekday, self.firstweekday + 7):
            yield weekdays % 7

    def itermonthdates(self, year, month):
        """Return an iterator for one month. The iterator will yield datetime.date
        values and will always iterate through complete weeks, so it will yield
        dates outside the specified month.
        """
        date = datetime.date(year, month, 1)

        # Go back to the beginning of the week
        days = (date.weekday() - self.firstweekday) % 7
        date -= datetime.timedelta(days=days)
        oneday = datetime.timedelta(days=1)

        while True:
            yield date
            try:
                date += oneday
            except OverflowError:
                # Adding one day could fail after datetime.MAXYEAR
                break
            if date.month != month and date.weekday() == self.firstweekday:
                break

    def itermonthdays2(self, year, month):
        """Like itermonthdates(), but will yield (day number, weekday number)
        tuples. For days outside the specified month the day number is 0.
        """
        for weekday, day in enumerate(self.itermonthdays(year, month), self.firstweekday):
            yield day, weekday % 7

    def itermonthdays(self, year, month):
        """Like itermonthdates(), but will yield day numbers. For days outside
        the specified month the day number is 0.
        """
        day1, ndays = monthrange(year, month)
        days_before = (day1 - self.firstweekday) % 7
        yield from repeat(0, days_before)
        yield from range(1, ndays + 1)
        days_after = (self.firstweekday - day1 - ndays) % 7
        yield from repeat(0, days_after)

    def monthdatescalendar(self, year, month):
        """Return a matrix (list of lists) representing a month's calendar.
        Each row represents a week; week entries are datetime.date values.
        """
        dates = list(self.itermonthdates(year, month))
        return [dates[i : i + 7] for i in range(0, len(dates), 7)]

    def monthdays2calendar(self, year, month):
        """Return a matrix representing a month's calendar.
        Each row represents a week; week entries are
        (day number, weekday number) tuples. Day numbers outside this month
        are zero.
        """
        days = list(self.itermonthdays2(year, month))
        return [days[i : i + 7] for i in range(0, len(days), 7)]

    def monthdayscalendar(self, year, month):
        """Return a matrix representing a month's calendar.
        Each row represents a week; days outside this month are zero.
        """
        days = list(self.itermonthdays(year, month))
        return [days[i : i + 7] for i in range(0, len(days), 7)]

    def yeardatescalendar(self, year, width=3):
        """Return the data for the specified year ready for formatting. The return
        value is a list of month rows. Each month row contains up to width months.
        Each month contains between 4 and 6 weeks and each week contains 1-7
        days. Days are datetime.date objects.
        """
        months = [self.monthdatescalendar(year, i) for i in range(JANUARY, JANUARY + 12)]
        return [months[i : i + width] for i in range(0, len(months), width)]

    def yeardays2calendar(self, year, width=3):
        """Return the data for the specified year ready for formatting (similar to
        yeardatescalendar()). Entries in the week lists are
        (day number, weekday number) tuples. Day numbers outside this month are
        zero.
        """
        months = [self.monthdays2calendar(year, i) for i in range(JANUARY, JANUARY + 12)]
        return [months[i : i + width] for i in range(0, len(months), width)]

    def yeardayscalendar(self, year, width=3):
        """Return the data for the specified year ready for formatting (similar to
        yeardatescalendar()). Entries in the week lists are day numbers.
        Day numbers outside this month are zero.
        """
        months = [self.monthdayscalendar(year, i) for i in range(JANUARY, JANUARY + 12)]
        return [months[i : i + width] for i in range(0, len(months), width)]


class HTMLCalendar(Calendar):
    """This calendar returns complete HTML pages."""

    # CSS classes for the day <td>s
    cssclasses = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    def formatday(self, day, weekday, theyear, themonth):
        """Return a day as a table cell."""
        if day == 0:
            return '<td class="day">&nbsp;</td>' # day outside month
        else:
            return f'<td class="day {self.cssclasses[weekday]}" id="_{theyear}{themonth:02d}{day:02d}">{day}</td>'

    def formatweek(self, theweek, theyear, themonth):
        """Return a complete week as a table row."""
        daycells = ''.join(
            self.formatday(day, weekday, theyear, themonth)
            for day, weekday in theweek
        )
        return f'<tr>{daycells}</tr>'

    def formatweekday(self, day):
        """Return a weekday name as a table header."""
        return f'<th class="{self.cssclasses[day]}">{day_abbr[day]}</th>'

    def formatweekheader(self):
        """Return a header for a week as a table row."""
        week = ''.join(self.formatweekday(i) for i in self.iterweekdays())
        return f'<tr>{week}</tr>'

    def formatmonthname(self, theyear, themonth, withyear=True):
        """Return a month name as a table row."""
        if withyear:
            month = f'{month_name[themonth]} {theyear}'
        else:
            month = month_name[themonth]
        return f'<tr><th colspan="7" class="month">{month}</th></tr>'

    def formatmonth(self, theyear, themonth, withyear=True):
        """Return a formatted month as a table."""
        content = []
        append = content.append
        append(f'<table class="month" id="{theyear}{themonth:02d}">\n')
        append(f"{self.formatmonthname(theyear, themonth, withyear=withyear)}\n")
        append(f"{self.formatweekheader()}\n")
        for week in self.monthdays2calendar(theyear, themonth):
            append(f"{self.formatweek(week, theyear, themonth)}\n")
        append('</table>\n')
        return ''.join(content)

    def formatyear(self, theyear, width=3):
        """Return a formatted year as a table of tables."""
        content = []
        append = content.append
        width = max(width, 1)
        append(f'<table class="year" id="{theyear}">\n')
        append(f'<tr><th colspan="{width}" class="year">{theyear}</th></tr>')
        for i in range(JANUARY, JANUARY + 12, width):
            # months in this row
            months = range(i, min(i + width, 13))
            append('<tr>')
            for month in months:
                append(f'<td>{self.formatmonth(theyear, month, withyear=False)}</td>')
            append('</tr>')
        append('</table>')
        return ''.join(content)

    def formatpage(self, startyear, endyear, css=""):
        return HTML_TEMPLATE.replace(
            "{{CONTENT}}",
            "<hr />\n".join(self.formatyear(year) for year in range(startyear, endyear + 1))
        ).replace("{{STYLE}}", css)
