from mrjob.job import MRJob
from urlparse import urlparse
from urlparse import parse_qs
from urllib2 import unquote

from MyFuzz import MainFuzz
from mrjob.protocol import PickleProtocol
from VulnIndex import IndexData


class FuzzDistributed(MRJob):
    INTERNAL_PROTOCOL = PickleProtocol

    def mapper(self, key, url):
        url = unquote(url)
        url_parsed = urlparse(url)
        domain = url_parsed.scheme + "://" + url_parsed.netloc + "/"

        url_query = url_parsed.query
        query_dict = parse_qs(url_query)

        mainfuzz = MainFuzz()

        for query_param, query_value in query_dict.iteritems():
            vul_list = mainfuzz.fuzz(url_parsed, query_param)
            print 'debug --->', vul_list
            yield domain, vul_list

    def reducer(self, domain, vuln_lists):
        full_vuln_list = []
        for vuln_list in vuln_lists:
            # print 'debug --->', vuln_list
            full_vuln_list = full_vuln_list + vuln_list

        print '\n ========== DEBUG HERE =============='
        # print '\n domain => ', domain
        # for vul in full_vuln_list:
        #     print 'type', vul.vul_type, 'url: ', vul.vul_url
        #Prepare for update document Solr in here
        print '[+] Index domain', domain
        index = IndexData(domain, full_vuln_list)
        index.add_data()

        yield domain, full_vuln_list

if __name__ == '__main__':
    FuzzDistributed.run()
