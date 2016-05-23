#!/usr/bin/env python
import requests, urllib2
import config

def paste(data):
    pastebins = {
        'sprunge': sprunge,
        'nnmm': nnmm,
        'sicpme': sicpme,
        'ix': ix,
    }
    return pastebins.get(getattr(config, 'PASTEBIN', ''), nnmm)(data)

def sprunge(data):
    sprunge_data = {"sprunge": data}
    response = requests.post("http://sprunge.us", data=sprunge_data)
    message = response.text.encode().strip('\n')
    return message

def nnmm(data):
    return urllib2.urlopen("https://nnmm.nl", data).read()

def sicpme(data):
    return requests.post('https://sicp.me/', data={'paste': data}).text.encode().strip('\r\n')

def ix(data):
    return requests.post('http://ix.io/', data={'f:1': data}).text.encode().strip('\r\n')
