#!/usr/bin/env python
import requests

def sprunge(data):
    sprunge_data = {"sprunge": data}
    response = requests.post("http://sprunge.us", data=sprunge_data)
    message = response.text.encode().strip('\n')
    return message

def pastebin(data):
    raise NotImplementedError
