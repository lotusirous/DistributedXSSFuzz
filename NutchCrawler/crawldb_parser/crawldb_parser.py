import os
import sys
import glob
import csv
import shutil

from urlparse import urlparse, parse_qs

cwdir = os.path.dirname(__file__)
myproject_base = os.path.join(cwdir, "..")
sys.path.append(os.path.join(myproject_base, "hadoop_connection"))

from ConfigParser import SafeConfigParser
config_parser = SafeConfigParser()
config_parser.read(
    os.path.join(myproject_base, 'main_config', 'main_config.cfg'))
hadoop_user = config_parser.get('users', 'hadoop_user')
NUTCH_HOME = config_parser.get('directories', 'NUTCH_HOME')
NUTCH_RUNTIME_DEPLOY = os.path.join(NUTCH_HOME, 'runtime', 'deploy')
from hadoop_connection import HadoopConnection

filelocation = os.path.join(myproject_base, "../WebFuzz")
filename = filelocation + '/url_to_fuzz.txt'


class CrawlDBParser(object):
    """
        CrawlDB operations.
    """
    def get_db_from_hdfs(self):
        # clear tmp directory
        myhadoop = HadoopConnection()
        print "\n Cleanning tmp directory..."
        tmpDir = myproject_base + '/tmp/mycrawl_output'
        try:
            shutil.rmtree(tmpDir)
            print 'Done. \n'
        except OSError:
            print 'tmp directory is empty, output directory is cleaned.'
        mycrawldb = "mycrawl_output"
        print "\n Getting mycrawl_output from hdfs... \n"
        return myhadoop.getFileFromHDFS(mycrawldb, tmpDir)

    def _genurl_from_csv(self):
        tmpDir = myproject_base + '/tmp/mycrawl_output/*'
        crawled_files = glob.glob(tmpDir)
        for crawled_file in crawled_files:
            with open(crawled_file, 'rb') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=';')
                next(spamreader, None)  # Skip header
                for row in spamreader:
                    yield row[0]

    def url_fuzz(self):
        list_of_keys = []
        url_list = []

        # prevent .js and .css with query.
        # to prevent .js?ver=1.23
        deny_list = ['.js', '.css']
        for url in self._genurl_from_csv():
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            path = parsed_url.path
            query_keys = parse_qs(parsed_url.query).keys()

            if not query_keys and domain not in list_of_keys:

                url_list.append(url)
                list_of_keys.append(domain)

            # key is concat query + path + domain
            # example: theme_id_/blog02.php_blog.chamberweb.jp

            url_keys = [x + '_' + path + '_' + domain for x in query_keys]

            if query_keys and url_keys not in list_of_keys:
                if parsed_url.path[-3:] not in deny_list:
                    if parsed_url.path[-4:] not in deny_list:
                        list_of_keys.append(url_keys)
                        url_list.append(url)

        return url_list

    def make_urlfuzz_file(self):
        """ check file if exists"""
        if os.path.isfile(filename):
            os.remove(filename)

        f = open(filename, "w")
        for url in self.url_fuzz():
            f.write(url + '\n')
        f.close()

# if __name__ == '__main__':
#     crawldb = CrawlDBParser()
#     crawldb.make_urlfuzz_file()
