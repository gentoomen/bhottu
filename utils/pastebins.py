#!/usr/bin/env python
import requests, urllib2

def sprunge(data):
    sprunge_data = {"sprunge": data}
    response = requests.post("http://sprunge.us", data=sprunge_data)
    message = response.text.encode().strip('\n')
    return message

def pastebin(data):
    raise NotImplementedError

def nnmm(data):
    return urllib2.urlopen("https://nnmm.nl", data).read()
