from payload_parser import GetPayload
from random import randint
from urllib import urlencode
from urllib import quote_plus
from urllib2 import unquote
from urlparse import urlunparse, urlparse, parse_qs
import requests
from lxml import html
from Vulnerability import Vulnerability


class BaseFuzz:
    """Series of methods for another Fuzz"""
    def __init__(self):
        self.getpayload = GetPayload()
        self.xss_payloads_raw = self.getpayload.get_xss_string()
        self.timeout = 4

    def _interpret_payload(self):
        """ translate __RANDOM_INT__ to useful variable"""
        self.random_int = randint(100, 3000)
        self.xss_payloads = [x.replace("__RANDOM_INT__", str(self.random_int)) for x in self.xss_payloads_raw]

    def prepend_payload(self, payload_list, str_to_prepend):
        """Prepend a string for every element in list,
           append to the old list and return a new list"""
        prepended_list = []
        for payload in payload_list:
            prepend_payload = str_to_prepend + payload
            prepended_list.append(prepend_payload)

        ret_list = payload_list + prepended_list
        return ret_list

    def urlencode_payload(self, list_to_encode):
        """Encode payload for by pass"""
        list_to_encode_copy = list(list_to_encode)
        list_encode = [quote_plus(x) for x in list_to_encode_copy]
        ret_list = list_to_encode_copy + list_encode

        return ret_list

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

        # print '>>>', payload
        assembled_query = urlencode(self.query_dict, doseq=True)
        assembled_query = unquote(assembled_query).decode('utf8')
        # print '>>>>', assembled_query ,'\n'

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
            r = requests.get(url, timeout=self.timeout)
            ret_text = r.text
        except:
            ret_text = 'Request timed out'

        # return (url, ret_text)
        return ret_text

    def find_string(self, html_text, find_string):
        tree = html.fromstring(html_text)
        flag = False
        for e in tree.xpath('//text()'):
            if e == find_string:
                flag = True
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
        vul_list = []
        for url in self.gen_url_payload(self.query_param, self.payload_list):
            # print '>> Fuzz url: ', url
            ret_text = self.url_response(url)
            matching_string = 'alert(' + str(self.random_int) + ')'
            if self.find_string(ret_text, matching_string):
                # print '....OK'
                myvul = Vulnerability('xss', url)
                vul_list.append(myvul)

        return vul_list


class MainFuzz(object):
    """Main class"""
    def __init__(self):
        self.xss = XSSFuzz()
        self.xss._make_xss_payloads()

    def fuzz(self, parsed_url, query_param):
        self.xss.set_target(parsed_url, query_param)
        vul_list = self.xss.fuzz()

        return vul_list


# def test():
#     myurl = 'http://www.stromsparen-blog.ch/?s=Suche'

#     url_parsed = urlparse(myurl)
#     query_dict = parse_qs(url_parsed.query)

#     mainfuzz = MainFuzz()

#     full_vul_list = []
#     for query_param, query_val in query_dict.iteritems():

#         vul_list = mainfuzz.fuzz(url_parsed, query_param)
#         full_vul_list += vul_list

#     print '\n [+] Result is: '
#     print type(full_vul_list)
#     for vul in full_vul_list:
#         print 'type', vul.vul_type, 'url: ', vul.vul_url


if __name__ == '__main__':
    test()
