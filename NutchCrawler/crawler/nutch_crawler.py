import os
import sys
from subprocess import CalledProcessError, check_output
cwdir = os.path.dirname(__file__)
myproject_base = os.path.join(cwdir, "../")
sys.path.append(os.path.join(myproject_base, "hadoop_connection"))

from ConfigParser import SafeConfigParser
config_parser = SafeConfigParser()
config_parser.read(
    os.path.join(myproject_base, 'main_config', 'main_config.cfg'))
NUTCH_HOME = config_parser.get('directories', 'NUTCH_HOME')
HADOOP_HOME = config_parser.get('directories', 'HADOOP_INSTALL')
NUTCH_RUNTIME_DEPLOY = os.path.join(NUTCH_HOME, "runtime", "deploy")

hadoop_user = config_parser.get('users', 'hadoop_user')
from hadoop_connection import HadoopConnection
crawl_name = "mycrawl"


class NutchController:
    """Some Nutch command"""
    def __clear_previous_crawl(self):
        """clear all data all HDFS"""
        connection = HadoopConnection()
        print "Clear_previous_crawl ..."
        if connection.checkFileExist(crawl_name):
            print '\n Cleaning previous ' + crawl_name + ' ...'
            print 'Done. \n'
            connection.removeDFSDirectory(crawl_name)
        if connection.checkFileExist("mycrawl_output"):
            print '\n Cleaning previous mycrawl_output...'
            print 'Done. \n'
            connection.removeDFSDirectory("mycrawl_output")


    def crawl(self):
        self.__clear_previous_crawl()
        topN = config_parser.get('performance', 'topN')
        depth = config_parser.get('performance', 'depth')

        nutch_job_config = config_parser.get('job', 'NUTCH_JOB')
        nutch_job = os.path.join(NUTCH_RUNTIME_DEPLOY, nutch_job_config)
        hadoop_bin = os.path.join(HADOOP_HOME, "bin", "hadoop")
        if topN.lower() == "all":
            shell_command = [hadoop_bin,"jar", nutch_job, "org.apache.nutch.crawl.Crawl", "urls", "-dir", crawl_name, "-depth", depth]
        else:
            shell_command = [hadoop_bin,"jar", nutch_job, "org.apache.nutch.crawl.Crawl", "urls", "-dir", crawl_name, "-depth", depth, "-topN", topN]
        try:
            print "Crawling website..."
            check_output(shell_command)
        except CalledProcessError:
            print 'An error has occurred while execute crawl command.'

    def dump_crawldb(self):
        nutch_bin = os.path.join(NUTCH_RUNTIME_DEPLOY, "bin", "nutch")
        hdfs_dump = crawl_name + "/crawldb"
        shell_command = [nutch_bin, "readdb", hdfs_dump, "-dump", "mycrawl_output", "-format", "csv"]
        try:
            print "\n Dumping db................."
            print shell_command
            check_output(shell_command)
        except CalledProcessError:
            print "Error on dump command."

# if __name__ == '__main__':
#     mynutch = NutchController()
#     mynutch.dump_crawldb()
