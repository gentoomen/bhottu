#!/usr/bin/env python
import pycurl
import StringIO

def ix(data):
    request = pycurl.Curl()
    buffer = StringIO.StringIO()
    request.setopt(pycurl.URL, 'http://ix.io')
    request.setopt(pycurl.WRITEFUNCTION, buffer.write)
    request.setopt(pycurl.HTTPPOST, [('f:1', (pycurl.FORM_CONTENTS, data))])
    request.perform()
    request.close()
    return buffer.getvalue()
