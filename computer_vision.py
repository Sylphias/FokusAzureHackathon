from __future__ import print_function
import time
import requests
import keys

_url = 'https://api.projectoxford.ai/vision/v1.0/ocr'
_key = keys.cv_key
_maxNumRetries = 10


def processRequest(json, data, headers, params):
    """
    Helper function to process the request to Project Oxford

    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """

    retries = 0
    result = None

    while True:

        response = requests.request('post', _url, json=json, data=data, headers=headers, params=params)

        if response.status_code == 429:

            print("Message: %s" % (response.json()['error']['message']))

            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()['error']['message']))

        break

    return result


def analyzeImages(img_url):
    # Computer Vision parameters
    # params = {'visualFeatures': 'Tags'}
    headers = dict()
    headers['Ocp-Apim-Subscription-Key'] = _key
    headers['Content-Type'] = 'application/json'
    json = {'url': img_url}
    data = None
    result = processRequest(json, data, headers,"")
    bounded = {}
    for outestBound in result[unicode("regions")]:
        for outerBound in outestBound[unicode('lines')]:
            bound = outestBound[unicode('boundingBox')]
            bounded[bound]  = [x[unicode('text')] for x in outerBound[unicode('words')]]
    return bounded

