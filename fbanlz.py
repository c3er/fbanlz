#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import datetime
import collections
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


class CountingDict(collections.UserDict):
    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            return 0

    def add(self, key):
        self[key] += 1


class StyleData:
    def __init__(self, id_, bgcolor):
        self.id = id_
        self.bgcolor = bgcolor

    def __str__(self):
        return f"#{self.id} {{ background-color: #{self.bgcolor}; }}"


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


def getdatecounts(dates):
    counts = CountingDict()
    for date in dates:
        counts.add((date.year, date.month, date.day))
    return counts


def getcellstyles(datecounts):
    DARKEST = 143
    step = DARKEST // max(datecounts.values())
    styles = []
    for date, count in datecounts.items():
        print(date, count)
        id = f"_{date[0]}{date[1]:02d}{date[2]:02d}"
        value = 255 - step * count
        bgcolor = hex(value)[2:] * 3
        styles.append(StyleData(id, bgcolor))
    return "\n".join(str(style) for style in styles)


def main():
    session_file = os.path.join(getstarterdir(), "fbdata", "html", "security.htm")
    datestrings = extract_datestrings(session_file)
    dates = parse_datestrings(datestrings)

    style = getcellstyles(getdatecounts(dates))

    years = [date.year for date in dates]
    startyear = min(years)
    endyear = max(years)

    cal = calendar.HTMLCalendar()
    with open(os.path.join(getstarterdir(), "logons.html"), "w", encoding="utf8") as f:
        f.write(cal.formatpage(startyear, endyear, style))


if __name__ == "__main__":
    main()
