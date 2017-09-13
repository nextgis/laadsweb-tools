#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------------------------------------------------------------------------
# laadsweb-downloader-v2.py
# Author: Maxim Dubinin (maxim.dubinin@nextgis.com)
# About: Process LAADSWeb previews list to download all selected images
# Created: 27.06.2014
# Updated: 03.08.2017
# Usage example: python laadsweb-downloader-v2.py LAADS_query.2017-08-03T08_39.csv /home/sim/work/laadsweb-tools/ /home/sim/work/laadsweb-tools/hdf/
# -----------------------------------------------------------------------------------------------------------------------------------------------


#Get CSV here https://ladsweb.modaps.eosdis.nasa.gov/search/imageViewer/42/MOD02QKM--6,MOD03--6/2017-07-01..2017-08-03/D/44.1,47.3,47.6,44.4/2725035273

import sys
import urllib2
import csv
from progressbar import *
from httplib import BadStatusLine,IncompleteRead
import socket
import glob

def console_out(text):
    #write httplib error messages to console
    time_current = datetime.datetime.now()
    timestamp = time_current.strftime('%Y-%m-%d %H:%M:%S')
    
    f_errors.write(timestamp + ": "+ text)

def get_file(url,fn):
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
            f = open(results_dir + fn,"wb")
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
    f_csv = sys.argv[1] #csv with hdfs
    previews_dir = sys.argv[2] #folder with previews
    results_dir = sys.argv[3] #folder with outputs
   
    os.chdir(previews_dir)
    previews = glob.glob('*.jpg')
    
    hrefs = []
    with open(f_csv, 'rb') as f:
        reader = csv.reader(f)
        for rec in reader:
            link = 'https://ladsweb.modaps.eosdis.nasa.gov' + rec[1]
            hrefs.append(link)
    
    pbar = ProgressBar(widgets=[Bar('=', '[', ']'), ' ', Counter(), " of " + str(len(previews)*2), ' ', ETA()]).start()
    pbar.maxval = len(previews)*2
    
    for preview in previews:
        datetime = preview.split('.')[1] + '.' + preview.split('.')[2]
        down_list = [s for s in hrefs if datetime in s]
        
        for down_link in down_list:
            if not os.path.exists(results_dir + down_link.split('/')[-1]):
                status = get_file(down_link,down_link.split('/')[-1])
            pbar.update(pbar.currval+1)
    pbar.finish()
    f_errors.close()
   