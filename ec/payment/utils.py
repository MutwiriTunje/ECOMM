import json
from urllib import response
import requests
from requests import auth
from requests.auth import HTTPBasicAuth
from datetime import datetime
from decouple import config

import base64


def generate_access_token():
    try:
        results = requests.get(config('ACCESS_TOKEN_URL'), auth=HTTPBasicAuth(config('MPESA_CONSUMER_KEY'),config('MPESA_CONSUMER_SECRET')))
        print("status Code:" + str(results.status_code))
        if results.status_code != 200:
            raise Exception('Failed to generate Access token')
        else:
            response = results.json()
            # if successful - response is json of expiry_in, access_token
            print(response)
            access_token = response["access_token"]
    except requests.exceptions.ConnectionError:
        raise Exception("Mpesa Connection Failed")
    except Exception:
        raise Exception("Access error!")
    return access_token

def get_current_time():
    current_time = datetime.now()
    formated_time = current_time.strftime("%Y%m%d%H%M%S")
    # ----
    # Timestamp of the transaction,
    # normaly in the formart of YEAR+MONTH+DATE+HOUR+MINUTE+SECOND (YYYYMMDDHHMMSS)
    # Each part should be atleast two digits apart from the year which takes four digits.
    return formated_time

def generate_password(date):
    # This is the password used for encrypting the request sent:
    #  A base64 encoded string.
    # (The base64 string is a combination of Shortcode+Passkey+Timestamp)

    thePassword = config('MPESA_EXPRESS_SHORTCODE') + config('MPESA_PASSKEY') + date
    encodedPass = base64.b64encode(thePassword.encode('ascii'))
    decodedPass = encodedPass.decode("utf-8")
    print(decodedPass)
    return decodedPass

def stk_push(amount, number):
    access_token = generate_access_token()
    timeStamp = get_current_time()
    password = generate_password(timeStamp)

    headers = {"Authorization":"Bearer %s" % access_token}
    # parameter required are in https://developer.safaricom.co.ke/APIs/MpesaExpressSimulate
    json_parameters = {
        'BusinessShortCode':config('MPESA_EXPRESS_SHORTCODE'),
        'Password':password,
        'Timestamp':timeStamp,
        'TransactionType':config('TRANSACTION_TYPE'),
        'Amount':amount,
        'PartyA':number,
        'PartyB':config('MPESA_EXPRESS_SHORTCODE'),
        'PhoneNumber':number,
        'CallBackURL':config('CALLBACK_URL'),
        'AccountReference':config('ACCOUNT_REFERENCE'),
        'TransactionDesc':config('TRANSACTION_DESCRIPTION'),
    }

    response = requests.post(config('STK_PUSH_URL'), json=json_parameters,headers=headers)

    responseString = response.text
    print(responseString)
    jsonResponse = json.loads(responseString)
    print(jsonResponse)
    # if stk push successful, you'll get a response with
    # MerchantRequestID, CheckoutRequestID, ResponseDescription
    # ResponseCode(with 0 meaning successful), CustomerMessage
    # https://developer.safaricom.co.ke/APIs/MpesaExpressSimulate

    #  if an error occurs, maybe callbackurl is invalid, number invalid
    # you'll receive
    # {'requestId': '68430-16891732-1', 'errorCode': '400.002.02', 'errorMessage': 'Bad Request - Invalid CallBackURL'}
    # or
    # {'requestId': '8454-31397579-1', 'errorCode': '400.002.02', 'errorMessage': 'Bad Request - Invalid PhoneNumber'}
    # check if jsonResponse has errorCode, if true, then .....

    if 'errorCode' in jsonResponse:
        #   checking if key-errorCode exists in jsonResponse
        # if true error has occured
        data = {
            "errorMessage":jsonResponse['errorMessage'],
        }
    else:
        data = {
            "MerchantRequestID":jsonResponse['MerchantRequestID'],
            "CheckoutRequestID":jsonResponse['CheckoutRequestID'],
            "ResponseDescription":jsonResponse['ResponseDescription'],
            "ResponseCode":jsonResponse['ResponseCode'],
        }


    return data

def timeConverter(time):
    datetimeVar = datetime.strptime(time, "%Y%m%d%H%M%S")
    return datetimeVar