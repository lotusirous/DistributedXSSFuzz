#!/usr/bin/env python
from random import randint
from urllib import urlencode
from urllib import quote_plus
from urllib2 import unquote
from urlparse import urlunparse, parse_qs

from multiprocessing import TimeoutError
from multiprocessing.pool import ThreadPool

import os
import sys

cwdir = os.path.dirname(__file__)
sys.path.append(cwdir)
sys.path.append(os.path.join(cwdir, "payload_dir"))

import requests

from lxml import html

# Need to import when running on distributed
# GetPayload (2 files)
import string
import random
from payload_parser import GetPayload


class XSSFuzz(object):
    """Some method for fuzzing XSS vuln"""
    def __init__(self):
        self.payloads_raw = GetPayload().get_xss_string()
        # interpret __RANDOM_INT__
        self.random_string = self.id_generator()
        self.xss_payloads = [x.replace("__RANDOM_INT__", str(self.random_string)) for x in self.payloads_raw]

    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def fromCharCode_payload(self):
        self.chars_code = [ord(c) for c in self.random_string]
        self.char_code = ','.join(str(c) for c in self.chars_code)
        self.replace_string = "String.fromCharCode(" + self.char_code + ")"

        return [x.replace("__RANDOM_INT__", str(self.replace_string)) for x in self.payloads_raw]
        # for c in

    def prepend_payload(self):
        self.payloads = self.xss_payloads + self.fromCharCode_payload()
        self.payload_copy = []
        for f in self.payloads:
            f = '">' + f
            self.payload_copy.append(f)
        return self.payloads + self.payload_copy

if __name__ == '__main__':

    xssfuzz = XSSFuzz()
    for pl in xssfuzz.prepend_payload():
        print pl

    # url =
