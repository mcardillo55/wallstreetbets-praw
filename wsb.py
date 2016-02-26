#!/usr/bin/env python

import praw
import re
from collections import Counter
import curses
import datetime
import yahoo_finance

EXCLUDE_LIST = ["I", "A", "YOLO", "IV", "US", "FUCK", "LOL", "RIP"]


def printTable(stdscr, maxY, numComments, shareData, c):
    global EXCLUDE_LIST
    y = 0
    stdscr.clear()
    for key, value in sorted(c.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        if (y < maxY - 1):
            if shareData[key].get_change()[0] is '+':
                printColor = curses.color_pair(1)
            else:
                printColor = curses.color_pair(2)
            stdscr.addstr(y, 0, "%s\t%d\t%s\t%s\t" % (key, value, shareData[key].get_price(), shareData[key].get_change()), printColor)
            y = y + 1
    stdscr.addstr(maxY-1, 0, "Last updated: %s\tComments parsed:%d" % (datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S"), numComments))
    stdscr.refresh()

def getShareData(num, c):
    '''
    Takes a counter c of symbols and counts and returns a dict with num amount
    of symbol and Share object pairs. Also does error checking to detect false
    symbols and removes them from c
    '''
    shareData = {}
    y = 0 
    for symbol, count in sorted(c.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        try:
            share = yahoo_finance.Share(symbol)
        except AttributeError:
            continue
        if share.get_change() is None:
        #Not a real symbol, remove and add to exclude list
            EXCLUDE_LIST.append(symbol)
            del c[symbol]
            continue
        shareData[symbol] = share
        if len(shareData) >= num:
            break;
        y = y + 1
    return shareData

def getAndParseComments(subreddit, commentsVisited, p, c):
    subredditComments = subreddit.get_comments(limit=1000)
    for comment in subredditComments:
        m = p.findall(comment.body)
        if m:
            if comment.id not in commentsVisited:
                for match in m:
                    if match not in EXCLUDE_LIST:
                        c.update([match])
                commentsVisited.append(comment.id)

def main(stdscr):
    global EXCLUDE_LIST

    stdscr.nodelay(1)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
    stdscr.addstr(0,0,"Fetching data, please wait...")
    stdscr.refresh()
    p = re.compile("\\b[^a-zA-Z0-9]?([A-Z]{1,4})[^a-zA-Z0-9]?\\b")
    r = praw.Reddit("wallstreetbets comment parser")
    subreddit = r.get_subreddit("wallstreetbets")
    c = Counter()
    commentsVisited = []

    while(True):
        if stdscr.getch() == ord('q'):
            break
        maxY, maxX = stdscr.getmaxyx()
        stdscr.refresh()

        getAndParseComments(subreddit, commentsVisited, p, c)
        shareData = getShareData(maxY-1, c)
        printTable(stdscr, maxY, len(commentsVisited), shareData, c)
        curses.napms(5000)

curses.wrapper(main)
