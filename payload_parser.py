from lxml import etree

import os
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
file_localtion = ROOT_PATH + "/" + "payload/fuzz_payload.xml"


class GetPayload:
    """ Get payload and parse from XML"""
    def __init__(self):
        self.__parser = etree.XMLParser(strip_cdata=False)
        self.tree = etree.parse(file_localtion, self.__parser)
        self.root = self.tree.getroot()

    def get_xss_string(self):
        xss_string_eletree = self.root.findall('xss_payload/xss_string')
        xss_string_list = [xss_string.text for xss_string in xss_string_eletree]

        return xss_string_list

# if __name__ == '__main__':
#     getpayload = GetPayload()
#     print getpayload.get_xss_string()
