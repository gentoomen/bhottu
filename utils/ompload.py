#!/usr/bin/env python
import pycurl
import string
import random
import sys

class _buffer(object):
    def __init__(self):
        self.data = ''
    def write(self, data):
        self.data += data
    def read(self):
        return self.data

def _ompload(postdata):
    request = pycurl.Curl()
    buffer = _buffer()
    request.setopt(pycurl.URL, 'http://omploader.org/upload')
    request.setopt(pycurl.WRITEFUNCTION, buffer.write)
    request.setopt(pycurl.HTTPPOST, postdata)
    request.perform()
    request.close()
    html = buffer.read()
    posBegin = html.find('<!-- View file:')
    posEnd = html.find('</a> -->')
    if posBegin < 0 or posEnd < 0:
        raise EnvironmentError, 'Unable to parse ompldr HTML'
    remainder = html[posBegin:posEnd]
    posUrl = remainder.find('http://')
    if posUrl < 0:
        raise EnvironmentError, 'Unable to parse ompldr HTML'
    return remainder[posUrl:]

def omploadData(data, filename = None):
    if filename == None:
        filename = ''.join(random.choice(string.ascii_lowercase) for x in range(10))
    return _ompload([('file1', (pycurl.FORM_CONTENTS, data, pycurl.FORM_FILENAME, filename))])

def omploadFile(file):
    return _ompload([('file1', (pycurl.FORM_FILE, file))])

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print "Usage: %s <file to ompload>" % sys.argv[0]
        sys.exit(0)
    filename = sys.argv[1]
    print omploadFile(filename)
