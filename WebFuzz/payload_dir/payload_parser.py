#!/usr/bin/env python
import sys
import os
cwdir = os.path.dirname(__file__)

sys.path.append(cwdir)

import xml.etree.ElementTree as ET


class GetPayload(object):
    """docstring for ParsePayload"""
    def __init__(self,):
        self.tree = ET.parse(os.path.join(cwdir, "fuzz_payload.xml"))

    def get_xss_string(self):

        xss_strings_elt = self.tree.findall('xss_payload/xss_string')
        xss_string_list = [xss_string.text for xss_string in xss_strings_elt]

        return xss_string_list

    def get_trav_string(self):
        trav_string_elt = self.tree.findall('trav_payload/trav_string')
        trav_string_list = [trav_string.text for trav_string in trav_string_elt]
        return trav_string_list

if __name__ == '__main__':
    pa = GetPayload()
    # print pa.get_xss_string()
    # for raw in  pa.get_trav_string():
    #     print raw
