import os
from subprocess import Popen, PIPE, check_output, CalledProcessError
from subprocess import STDOUT
cwdir = os.path.dirname(__file__)
myproject_base = os.path.join(cwdir, "../")

from ConfigParser import SafeConfigParser
config_parser = SafeConfigParser()
config_parser.read(
    os.path.join(myproject_base, 'main_config', 'main_config.cfg'))
HADOOP_INSTALL = config_parser.get('directories', 'HADOOP_INSTALL')
NUTCH_HOME = config_parser.get('directories', 'NUTCH_HOME')
JAVA_HOME = config_parser.get('directories', 'JAVA_HOME')
hadoop_user = config_parser.get('users', 'hadoop_user')


class HadoopConnection:

    """
        Hadoop operations.
    """

    def __init__(self):
        self.hadoop_bin = os.path.join(HADOOP_INSTALL, 'bin', 'hadoop')
        self.hdfs_base = '/user/' + hadoop_user

    def checkConnection(self):
        """
            check hadooop process is running by using jps command
            return True, False
        """
        status = False
        jps_command = JAVA_HOME + '/bin/jps'
        tmp = os.popen(jps_command).read()

        if tmp.find("NameNode") != -1:
            status = True
        return status

    def checkFileExist(self, file_name):
        """
            check file name is exits
            return True if file is exits, else False
        """
        status = False
        shell_command = [self.hadoop_bin, 'dfs', '-ls', file_name]
        try:
            check_output(shell_command, stderr=STDOUT)
            status = True
        except CalledProcessError:
            pass
        return status

    def getFileFromHDFS(self, src_hdfs, dst_local):
        """
            return True if get successfully
            False if it has some error
        """
        status = False
        src_hdfs = self.hdfs_base + '/' + src_hdfs
        shell_command = [self.hadoop_bin, 'dfs', '-get', src_hdfs, dst_local]
        try:
            check_output(shell_command)
            status = True
        except CalledProcessError, e:
            print 'An error has occurred while GET file from HDFS.'
            print e
        return status

    def putFileToHDFS(self, src_local, dst_hdfs):
        """
            return True if PUT successfully
            False if it has some error
        """
        status = False
        dst_hdfs = self.hdfs_base + '/' + dst_hdfs
        shell_command = [self.hadoop_bin, 'dfs', '-put', src_local, dst_hdfs]
        try:
            check_output(shell_command)
            status = True
        except CalledProcessError:
            print 'An error has occurred while PUT file to HDFS.'
        return status

    def removeDFSDirectory(self, dst_hdfs):
        status = False
        dst_hdfs = self.hdfs_base + '/' + dst_hdfs
        shell_command = [self.hadoop_bin, 'dfs', '-rmr', dst_hdfs]
        try:
            check_output(shell_command)
            status = True
        except CalledProcessError:
            print 'An error has occurred while DELETE file from HDFS.'
        return status

if __name__ == '__main__':
    conn = HadoopConnection()
    print conn.checkConnection()
