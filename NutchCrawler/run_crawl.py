import os
import sys
myproject_base = os.path.dirname(__file__)
sys.path.append(os.path.join(myproject_base, "hadoop_connection"))
from hadoop_connection import HadoopConnection
sys.path.append(os.path.join(myproject_base, "crawler"))
from nutch_crawler import NutchController
sys.path.append(os.path.join(myproject_base, "crawldb_parser"))
from crawldb_parser import CrawlDBParser


def main():
    #sau khi nguoi dung da chinh regex-urlfilter va urls/seed.txt
    connect_hadoop = HadoopConnection()
    nutch_control = NutchController()
    crawldb_parse = CrawlDBParser()

    if not connect_hadoop.checkConnection():
        print "[x] Connections error !!!"
    else:
        try:
            nutch_control.crawl()
            nutch_control.dump_crawldb()
            crawldb_parse.get_db_from_hdfs()
            crawldb_parse.make_urlfuzz_file()
        except:
            print '\n [x] Error on main file'


if __name__ == '__main__':
    main()
