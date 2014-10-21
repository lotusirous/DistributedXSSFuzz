Distributed XSS Fuzzing
==================

Distributed XSS fuzz on hadoop using Nutch and Solr

Requires
------------------

* Nutch 1.7
* Solr 4.10.1 (lastest version)
* Hadoop 1.2.1

Setup
------------------
Setup Nutch running on hadoop using map-reduce in [this tutorial](http://ranithsachin.blogspot.com/2014/04/building-search-engine-with-nutch-solr.html)

Setup Solr:
1. Download lastest Solr from [apache](http://lucene.apache.org/solr/)
2. Extract Solr: tar zxvf solr
3. Go to example solr: cd solr/example/..

Running on Hadoop
------------------
1. Copy project to all nodes.
2. Export PYTHONPATH.
    Example: `export PYTHONPATH=/home/haduser/myenv/WebFuzz:/home/haduser/myenv/WebFuzz/payload_dir`
3. Run by command:
```
python DistributedJob.py -r hadoop \
--file payload_dir/fuzz_payload.xml \
--file payload_dir/payload_parser.py \
--file FuzzURL.py \
--file VulnIndex.py < demo.txt`
```
