#!/usr/bin/env python

import praw
import re
from collections import Counter
import curses
import datetime
import yahoo_finance


def printTable(stdscr, maxY, c):
    y = 0
    stdscr.clear()
    for key, value in sorted(c.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        if (y < maxY - 1):
            share = yahoo_finance.Share(key)
            if share.get_price() is not None:
                if share.get_change()[0] is '+':
                    stdscr.addstr(y, 0, key + "\t" + str(value) + "\t" + str(share.get_price()) + "\t" + str(share.get_change() + "\t"), curses.color_pair(1))
                else:
                    stdscr.addstr(y, 0, key + "\t" + str(value) + "\t" + str(share.get_price()) + "\t" + str(share.get_change() + "\t"), curses.color_pair(2))
                y = y + 1
    stdscr.addstr(maxY-1, 0, "Last updated: " + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S"))
    stdscr.refresh()

def main(stdscr):
    EXCLUDE_LIST = ["I", "A", "YOLO", "IV", "US", "FUCK", "LOL", "RIP"]

    stdscr.nodelay(1)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
    stdscr.addstr(0,0,"Fetching data, please wait...")
    p = re.compile("\\b[^a-zA-Z0-9]?([A-Z]{1,4})[^a-zA-Z0-9]?\\b")

    r = praw.Reddit("wallstreetbets comment parser")
    subreddit = r.get_subreddit("wallstreetbets")

    maxY, maxX = stdscr.getmaxyx()
    c = Counter()
    commentsVisited = []

    while(True):
        if stdscr.getch() == ord('q'):
            break
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
        curses.napms(5000)

curses.wrapper(main)