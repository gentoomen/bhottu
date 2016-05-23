#!/usr/bin/env python
import requests, urllib2
import config

def paste(data):
    if config.PASTEBIN == 'sprunge':
        return sprunge(data)
    if config.PASTEBIN == 'nnmm':
        return nnmm(data)
    if config.PASTEBIN == 'sicpme':
        return sicpme(data)
    if config.PASTEBIN == 'ix':
        return ix(data)
    raise NotImplementedError

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
