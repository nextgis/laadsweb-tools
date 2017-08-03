#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# laadsweb-preview-extractor.py
# Author: Maxim Dubinin (maxim.dubinin@nextgis.com)
# About: Process LAADSWeb output to download preview images
# Created: 25.06.2014
# Updated: 03.08.2017
# Usage example: python laadsweb-preview-extractor.py
# ---------------------------------------------------------------------------

import urllib2
import csv,sys
from progressbar import *
from httplib import BadStatusLine,IncompleteRead
import socket
import requests

WEB_API_FILES = 'https://ladsweb.modaps.eosdis.nasa.gov/api/v1/files/product={0}&collection={1}&dateRanges={2}..{3}&areaOfInterest=x{4}y{5},x{6}y{7}&dayCoverage={8}'
WEB_API_PREVIEWS = 'https://ladsweb.modaps.eosdis.nasa.gov/api/v1/imageFiles/'

def console_out(text):
    #write httplib error messages to console
    time_current = datetime.datetime.now()
    timestamp = time_current.strftime('%Y-%m-%d %H:%M:%S')
    
    f_errors.write(timestamp + ": "+ text)


def get_images(product, collection, date_begin, date_end, area, day_coverage):
    """
    Get array of images and previews
    :param product: Example 'MOD02QKM'
    :param collection: Example '6'
    :param date_begin: Example '2017-07-01'
    :param date_end: Example '2017-08-03'
    :param area: Set of coords: (x_min, y_min, x_max, y_max)
    :param day_coverage: 'true' or 'false'
    :return:
    """
    session = requests.session()

    # get images
    image_url = WEB_API_FILES.format(product, collection, date_begin, date_end, area[0], area[1], area[2], area[3], day_coverage)
    img_resp = session.get(image_url).json()

    # get previews
    ids = img_resp.keys()
    prev_resp = session.post(WEB_API_PREVIEWS, data={'fileIds': str(','.join(ids)),}).json()

    # make dict
    result = {}
    for key,image_info in img_resp.items():
        result[key] = {
            'name': image_info['name'],
            'image_url': image_info['fileURL'],
            'prev_url': prev_resp[key][0]['URL'] + '\/' + prev_resp[key][0]['FileName'] if key in prev_resp.keys() else None
        }

    return result


def download_preview(url,fn):
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
    #Create array of links to previews
    images = get_images('MOD02QKM', 6, '2017-07-01', '2017-08-03', (44.1, 47.3, 47.6, 44.4), 'true')

    
    pbar = ProgressBar(widgets=[Bar('=', '[', ']'), ' ', Counter(), " of " + str(len(images)), ' ', ETA()]).start()
    pbar.maxval = len(images)
    
    for k,v in images.items():
        fn = v['prev_url'].split('/')[-1]
        href = 'https://ladsweb.modaps.eosdis.nasa.gov' + v['prev_url']
        href = href.replace('\/','/')
        status = download_preview(href,fn)
        pbar.update(pbar.currval+1)

    pbar.finish()
   