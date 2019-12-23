#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib,datetime
import hmac,hashlib,base64
import http.client
import configparser
from urllib import parse


def mycmp(x, y):
    x0 = x.split("=")[0]
    y0 = y.split("=")[0]
    if x0 < y0:
        return -1
    if x0 == y0:
        return 0
    return 1

def doSignV2(cfg, data):
    res = parse.urlparse(cfg.endpoint)
    stringToSign = cfg.method + "\n"
    stringToSign += res.netloc + "\n"
    if res.path == "":
        stringToSign += "/\n"
    else:
        stringToSign += res.path + "\n"
    from functools import cmp_to_key
    items = data.split("&")
    items.sort(key=cmp_to_key(lambda x,y:mycmp(x,y)))
    
    stringToSign += "&".join(items)
    return base64.b64encode(hmac.new(bytes(cfg.secretKey,'utf-8'), bytes(stringToSign,'utf-8'), hashlib.sha256).digest())

def timeStamp():
    dt = datetime.datetime.utcnow().isoformat()
    return dt.split('.')[0] + ".000Z"

def time2str(dt):
    str = dt.isoformat()
    return str.split('.')[0] + ".000Z"

def gethost(url):
    res = parse.urlparse(url)
    return res.netloc


class config():
    endpoint = "http://127.0.0.1"
    accessKey = "1"
    secretKey = "1"
    version = "2009-08-15"
    signVersion = "2"
    method = "POST"
    signMethod = "HmacSHA256"


class bcclient():
    def __init__(self, confSection='cloud', debug=False):
        self.cfg = config()
        self.debug = debug
        cp = configparser .RawConfigParser()
        cp.read('cloud.cfg')
        
        self.cfg.endpoint = cp.get(confSection, 'Endpoint')
        self.cfg.accessKey = cp.get(confSection, 'AWSAccessKeyId')
        self.cfg.secretKey = cp.get(confSection, 'SecretAccessKey')

    def invoke(self, action, params):
        data = urllib.parse.urlencode({"Action":action})
        if len(params) > 0:
            data += "&" + urllib.parse.urlencode(params)

        ts = timeStamp()
        commons = {"Timestamp":ts,"AWSAccessKeyId":self.cfg.accessKey,"Version":self.cfg.version,"SignatureVersion":self.cfg.signVersion,"SignatureMethod":self.cfg.signMethod}
        data += "&" + urllib.parse.urlencode(commons)

        signVal = doSignV2(self.cfg, data)
        data += "&" + urllib.parse.urlencode({"Signature":signVal})

        host = gethost(self.cfg.endpoint)

        if self.debug == True:
            print('%s?\n%s\n' % (self.cfg.endpoint, data))

        conn = http.client.HTTPConnection(host)
        conn.request(self.cfg.method, self.cfg.endpoint, data)
        response = conn.getresponse()
        return response.read()