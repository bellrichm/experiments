import json
import sys
import urllib.request

def test_get():
    url = 'http://localhost:5000/api/v1/stations'
    request = urllib.request.Request(url)

    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as http_error:
        print(http_error)
        with http_error.fp:
            raw_data = http_error.read()
            print(raw_data)
            error_msg = raw_data.decode()
            print(error_msg)

def test_post():
    url = 'http://localhost:5000/api/v2/stations/'

    body = {
        'station_url': 'example.com',
        }
    json_body = json.dumps(body)

    request = urllib.request.Request(url)
    request.add_header('Content-Type', 'application/json')

    try:
        response = urllib.request.urlopen(request, data=json_body.encode('utf-8'))
    except urllib.error.HTTPError as http_error:
        print(http_error)
        raw_data = http_error.read()
        #raw_data = http_error.fp.read()
        print(raw_data)
        error_msg = raw_data.decode()
        print(error_msg)

if __name__=="__main__":
    print(f"Using Python {sys.version}")
    #test_get()
    test_post()
