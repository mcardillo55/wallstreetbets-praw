#!/usr/bin/env python

import praw
import re
import time
from collections import Counter
import curses
import datetime


def printTable(stdscr, maxY, c):
    y = 0
    stdscr.clear()
    for key, value in sorted(c.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        if (y < maxY - 1):
            stdscr.addstr(y, 0, key + "\t" + str(value)) 
            y = y + 1
    stdscr.addstr(maxY-1, 0, "Last updated: " + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S"))
    stdscr.refresh()

def main(stdscr):
    EXCLUDE_LIST = ["I", "A", "YOLO", "IV", "US", "FUCK", "LOL", "RIP"]
    p = re.compile("\\b[^a-zA-Z0-9]?([A-Z]{1,4})[^a-zA-Z0-9]?\\b")

    r = praw.Reddit("wallstreetbets comment parser")

    stdscr.addstr(0,0,"Fetching data, please wait...")
    subreddit = r.get_subreddit("wallstreetbets")

    maxY, maxX = stdscr.getmaxyx()
    c = Counter()
    commentsVisited = []
    lastComments = None

    while(True):
        maxY, maxX = stdscr.getmaxyx()
        stdscr.refresh()
        subredditComments = subreddit.get_comments(limit=1000)
        for comment in subredditComments:
            m = p.findall(comment.body)
            if m:
                if comment.id not in commentsVisited:
                    for match in m:
                        if match not in EXCLUDE_LIST:
                            c.update([match])
                    commentsVisited.append(comment.id)
        printTable(stdscr, maxY, c)
        time.sleep(5)

curses.wrapper(main)