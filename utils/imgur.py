#!/usr/bin/env python
import pycurl
import string
import sys
import base64

IMGUR_API_KEY=''    #register anon api code @ http://imgur.com/register/api_anon
                    #+ gets 50 uploads per hour

class _buffer(object):
    def __init__(self):
        self.data = ''
    def write(self, data):
        self.data += data
    def read(self):
        return self.data

def _imgur(postdata):
    request = pycurl.Curl()
    buffer = _buffer()
    request.setopt(pycurl.URL, 'http://api.imgur.com/2/upload.xml')
    request.setopt(pycurl.WRITEFUNCTION, buffer.write)
    request.setopt(pycurl.HTTPPOST, postdata)
    request.perform()
    request.close()
    xml = buffer.read()
    posBegin = xml.find('<original>')
    posEnd = xml.find('</original>')
    if posBegin < 0 or posEnd < 0:
        raise EnvironmentError, 'Unable to parse imgur XML'
    remainder = xml[posBegin:posEnd]
    posUrl = remainder.find('http://')
    if posUrl < 0:
        raise EnvironmentError, 'Unable to parse imgur XML'
    return remainder[posUrl:]

def imgurData(imageData):
    return _imgur([('key', IMGUR_API_KEY), ('image', base64.b64encode(imageData))])

def imgurFile(file):
    return _imgur([('key', IMGUR_API_KEY), ('image', (pycurl.FORM_FILE, file)) ])

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print "Usage: %s <image to upload>" % sys.argv[0]
        sys.exit(0)
    filename = sys.argv[1]
    print imgurFile(filename)
