#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# laadsweb-preview-extractor.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# About: Process LAADSWeb output to download preview images
# Created: 25.06.2014
# Usage example: python laadsweb-preview-extractor.py
# ---------------------------------------------------------------------------

from bs4 import BeautifulSoup
import urllib2
import csv
from progressbar import *
from httplib import BadStatusLine,IncompleteRead
import socket

def console_out(text):
    #write httplib error messages to console
    time_current = datetime.datetime.now()
    timestamp = time_current.strftime('%Y-%m-%d %H:%M:%S')
    
    f_errors.write(timestamp + ": "+ text)

def get_preview(url,fn):
    numtries = 5
    timeoutvalue = 40
    
    for i in range(1,numtries+1):
        i = str(i)
        try:
            u = urllib2.urlopen(url, timeout = timeoutvalue)
        except BadStatusLine:
            console_out('BadStatusLine for:' + url + '.' + ' Attempt: ' + i)
            res = False
            time.sleep(3)
        except urllib2.URLError, e:
            get_photo_status = False
            if hasattr(e, 'reason'):
                console_out('We failed to reach a server for:' + url + ' Reason: ' + str(e.reason) + '.' + ' Attempt: ' + i)
            elif hasattr(e, 'code'):
                console_out('The server couldn\'t fulfill the request for: ' + url + ' Error code: ' + str(e.code) + '.' + ' Attempt: ' + i)
            res = False
            time.sleep(3)
        except socket.timeout, e:
            console_out('Connection timed out on urlopen() for: ' + url + '.' + ' Attempt: ' + i)
            res = False
            time.sleep(3)
        else:
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            f = open(fn,"wb")
            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
                status = r"%10d [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
                status = status + chr(8)*(len(status)+1)
                #print status,

            f.close()
            get_photo_status = True
            break
    
    return get_photo_status
    
if __name__ == '__main__':
    #init errors.log
    f_errors = open("errors.txt","wb")

    f = open('page.htm','rb')
    soup = BeautifulSoup(''.join(f.read()))
    links_all = soup.findAll("a", { "target" : "popup" })
    
    hrefs = []
    for link in links_all:
        if link.text.strip() == '+ View RGB':
            hrefs.append(link['href'])
    
    pbar = ProgressBar(widgets=[Bar('=', '[', ']'), ' ', Counter(), " of " + str(len(hrefs)), ' ', ETA()]).start()
    pbar.maxval = len(hrefs)
    
    for href in hrefs:
        fn = href.split('/')[-1]
        status = get_preview(href,fn)
        pbar.update(pbar.currval+1)
    pbar.finish()
    f_errors.close()
   