import os
from dotenv import load_dotenv
import requests
import uuid
import json
from xero.auth import PublicCredentials

load_dotenv()


# Generic API Sending

def make_api_call(method, url, credential, payload=None, parameters=None):
    # Send these headers with all API calls
    headers = {
        'Accept': 'application/json',

    }
    # Use these headers to instrument calls. Makes it easier
    # to correlate requests and responses in case of problems
    # and is a recommended best practice.
    
    request_id = str(uuid.uuid4())
    instrumentation = {'client-request-id': request_id,
                       'return-client-request-id': 'true'}

    headers.update(instrumentation)

    response = None

    if (method.upper() == 'GET'):
        response = requests.get(url, headers=headers, params=parameters,auth=credential )
    elif (method.upper() == 'DELETE'):
        response = requests.delete(url, headers=headers, params=parameters, auth=credential)
    elif (method.upper() == 'PATCH'):
        headers.update({'Content-Type': 'application/json'})
        response = requests.patch(url, headers=headers, data=json.dumps(payload), params=parameters, auth=credential)
    elif (method.upper() == 'POST'):
        headers.update({'Content-Type': 'application/json'})
        response = requests.post(url, headers=headers, data=json.dumps(payload), params=parameters, auth=credential)

    return response


def xero_asset_put(credential, data):
    url = "https://api.xero.com/assets.xro/1.0/Assets"
    r = make_api_call('POST', url, credential, data, None)
    if (r.status_code == requests.codes.ok):
        return r.json()
    else:
        return "{0}: {1}".format(r.status_code, r.text)


def xero_asset_get(credential, parameters):
    url = "https://api.xero.com/assets.xro/1.0/Assets"
    r = make_api_call('GET', url, credential, None, parameters)
    if (r.status_code == requests.codes.ok):
        return r.json()
    else:
        return "{0}: {1}".format(r.status_code, r.text)


def main():
    privateKey = os.getenv("XERO_PRIVATE_KEY")
    privateConsumerKey = os.getenv("XERO_PRIVATE_CONSUMER_KEY")

    if privateKey is None or privateConsumerKey is None:
        raise KeyError(
            'Please define both XERO_CONSUMER_KEY and XERO_CONSUMER_SECRET environment variables')

    credentials = PublicCredentials(privateKey, privateConsumerKey)
    print("please go here and authorize", credentials.url)

    verifier = input('paste verifier here:')

    credentials.verify(verifier)

    data = {
        "assetName": "Other Computer Test",
        "assetNumber": "FA-00211"
    }

    credentials.expired()
    print(xero_asset_put(credentials.oauth, data))
    print(xero_asset_get(credentials.oauth, {"status": "DRAFT"}))

    return 0


if __name__ == '__main__':
    main()
