#!/usr/bin/env python
import pycurl
import StringIO

def pastebin(data):
    request = pycurl.Curl()
    buffer = StringIO.StringIO()
    request.setopt(pycurl.URL, 'http://sprunge.us')
    request.setopt(pycurl.WRITEFUNCTION, buffer.write)
    request.setopt(pycurl.HTTPPOST,
	    [('sprunge', (pycurl.FORM_CONTENTS, data))])
    request.perform()
    request.close()
    return buffer.getvalue()
