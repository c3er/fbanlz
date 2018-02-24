#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import datetime
import xml.etree.ElementTree as et
import calendar


MONTHS = [
    "Januar",
    "Februar",
    "März",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
]


def getstarterdir():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def extract_datestrings(file):
    root = et.parse(file).getroot()

    # "element.text" returns only the first text node.
    # Because the text nodes are splitted by "<br />" tags, they would be retrieved by calling
    # "element.tail" of these "<br />" tags.
    return [element.text for element in root.findall("body/div[@class='contents']/ul[2]/li/p")]


def parse_datestrings(datestrings):
    dates = []
    for datestring in datestrings:
        parts = datestring.split()
        hour, minute = [int(val) for val in parts[5].split(":")]
        dates.append(datetime.datetime(
            int(parts[3]),
            MONTHS.index(parts[2]) + 1,
            int(parts[1][:-1]),
            hour,
            minute
        ))
    return dates


def main():
    session_file = os.path.join(getstarterdir(), "fbdata", "html", "security.htm")
    datestrings = extract_datestrings(session_file)
    dates = parse_datestrings(datestrings)

    years = [date.year for date in dates]
    startyear = min(years)
    endyear = max(years)

    cal = calendar.HTMLCalendar()
    with open(os.path.join(getstarterdir(), "logons.html"), "w", encoding="utf8") as f:
        f.write(cal.formatpage(startyear, endyear))


if __name__ == "__main__":
    main()
