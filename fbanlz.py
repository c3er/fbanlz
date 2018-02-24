#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import xml.etree.ElementTree as et


def getstarterdir():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def extract_datestrings(file):
    root = et.parse(file).getroot()

    # "element.text" returns only the first text node.
    # Because the text nodes are splitted by "<br />" tags, they would be retrieved by calling
    # "element.tail" of these "<br />" tags.
    return [element.text for element in root.findall("body/div[@class='contents']/ul[2]/li/p")]


def main():
    session_file = os.path.join(getstarterdir(), "fbdata", "html", "security.htm")
    datestrings = extract_datestrings(session_file)
    for date in datestrings:
        print(date)


if __name__ == "__main__":
    main()
