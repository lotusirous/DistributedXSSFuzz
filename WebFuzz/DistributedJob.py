import os
import sys
from mrjob.job import MRJob
cwdir = os.path.dirname(__file__)
payload_dir = os.path.join(cwdir, "payload_dir")
sys.path.append(cwdir)
sys.path.append(payload_dir)

from VulnIndex import IndexData
from FuzzURL import MainFuzz

from urlparse import urlparse
from urlparse import parse_qs


class TestListJob(MRJob):

    def mapper(self, _, line):
        domain = urlparse(line).netloc
        # Check if url have query
        self.set_status("[+] Fuzzing...." + line)
        if urlparse(line).query:
            url_vul_list = maperfuzz(line)
            yield domain, url_vul_list

    def reducer(self, domain, values):
        full_list = []
        for val in values:
            full_list += val

        self.set_status("Indexing..." + domain)
        index = IndexData(domain, full_list)
        index.add_data()

        yield domain, full_list


def maperfuzz(url_input):
    url_parsed = urlparse(url_input)
    query_dict = parse_qs(url_parsed.query)

    mainfuzz = MainFuzz()

    full_vul_list = []
    for query_param, query_val in query_dict.iteritems():

        vul_list = mainfuzz.fuzz(url_parsed, query_param)
        full_vul_list += vul_list
    return full_vul_list


if __name__ == '__main__':
    TestListJob.run()
