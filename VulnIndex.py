import pysolr
from urlparse import urlparse


summary_url = 'http://localhost:8983/solr/vul_summary'
detail_url = 'http://localhost:8983/solr/vul_detail'

# from Vulnerability import Vulnerability
# from random import choice
# from random import randint
# from string import letters

# def make_vul_list():
#     list_vuln = []
#     for i in range(1, 10):
#         if i == randint(1, 10):
#             myvul = Vulnerability('xss', make_domain() + '<script>' + choice(letters))
#         else:
#             myvul = Vulnerability('path_traversal', make_domain() + '<script>' + choice(letters))

#         list_vuln.append(myvul)
#     return list_vuln


# def make_domain():
#     name = "http://www."
#     domain = ""
#     for i in range(1, 5):
#         domain += choice(letters)

#     suff_fix = [".com", ".org", ".net", ".edu.vn"]
#     ret = name + domain + choice(suff_fix)
#     return ret.lower()


class IndexData(object):
    """Some fuction for manipulate with Solr
        solr summary id: com.google.www.9
            with 9 is number of vulnerability
        solr detail id : com.google.www.(0-8)
            with 0 is number from 0 to 8
    """
    def __init__(self, domain, vuln_list):
        self.domain = domain
        self.vuln_list = vuln_list
        self.id_dom_sum = self.__reverse_domain(self.domain) + str(len(vuln_list))
        self.id_dom_detail = self.__reverse_domain(self.domain)

    def __reverse_domain(self, domain_name):
        """ Reverse for search faster
        ex: www.google.com -> com.google.www
        """
        domain = urlparse(domain_name).netloc
        tmp = domain.split('.')[::-1]
        reversed_domain = ""
        for e in tmp:
            reversed_domain += e + '.'

        return reversed_domain

    def _add_detail(self):
        con_detail = pysolr.Solr(detail_url)

        id_c = 0
        final_list = []
        for vuln in self.vuln_list:
            base_id = self.id_dom_detail + str(id_c)

            up_data = {}
            up_data['id'] = base_id
            up_data['vuln_type'] = vuln.vul_type
            up_data['vuln_url'] = vuln.vul_url

            final_list.append(up_data)
            id_c += 1

        try:
            print '\n [+] Add data to Solr detail....'
            con_detail.add(final_list)
        except Exception, e:
            print '\n [x] Failure to add data to Solr Detail: \n %s ' % e

    def _add_summary(self):
        con_sum = pysolr.Solr(summary_url)
        xss_num = 0
        path_num = 0
        for vul_num in self.vuln_list:
            if vul_num.vul_type == 'xss':
                xss_num += 1
            if vul_num.vul_type == 'path_traversal':
                path_num += 1

        try:
            print '\n [+] Add data to Solr Summary....'
            # pysolr using list for add data
            upload_data = []
            data = {}

            data['id'] = self.id_dom_sum
            data['name'] = self.domain
            data['xss_num'] = xss_num
            data['path_num'] = path_num
            # add data
            upload_data.append(data)

            con_sum.add(upload_data)

        except Exception, e:
            print '\n [x] Failure to add data to Solr Server \n %s' % e

    def add_data(self):
        # print '[+] Indexing', self.domain
        self._add_detail()
        self._add_summary()

# if __name__ == '__main__':
#     domain = make_domain()
#     vuln_list = make_vul_list()
#     indexdata = IndexData(domain, vuln_list)
#     indexdata.add_data()
