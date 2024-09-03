from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt


from .utils import stk_push, timeConverter
from ast import literal_eval
from .models import *

# Create your views here.


@api_view(['POST'])
def makepayment(request):
    # { "phoneNumber":"254706803305", "amount":"1"}
    data = request.data
    print(data)
    amount = float(data['amount'])
    phoneNumber = data['phoneNumber']
    # Handle number validation/changing it to 254*** on client side
    try:
        response = stk_push(amount=amount,number=phoneNumber)
    except Exception as e:
        print(e)
        # email or text admin there is a problem with generating access token
        return Response({'errorMessage':'Error! Try Again Later.'})
    # print("the response")
    # print(response)
    # print("--0---")
    if 'errorMessage' in response:
        # print('error has occured')
        # unlock the products
        if response['errorMessage'] == 'Bad Request - Invalid PhoneNumber':
            return Response({'errorMessage':'Error! Invalid Phone Number. Edit in Profile, 254*********.'})
        else:
            # email or text admin there is a problem with callbackurl to resolve issue fast
            return Response({'errorMessage':'Error! Try Again Later.'})

    elif response['ResponseCode'] != '0':
        # unlock the products
        return Response({'errorMessage':'Error! Try Again Later.'})
    else:
        # stk_push successful, add MerchId, and the order details to a ordersToAdd table
        merchId = response['MerchantRequestID']

    # stk_push successful , NOW USE THE MerchantRequestID TO CHECK PROGRESS
    return Response({'merchId':merchId})

@api_view(['POST'])
def processingPayment(request):
    # function initiated by callBack Url, processes data sent by Daraja
    data = request.data
    print(data)
    body = data['Body']
    stkcallback = body['stkCallback']

    MerchantRequestID = stkcallback['MerchantRequestID']
    resultCode = stkcallback['ResultCode']
    resultDesc = stkcallback['ResultDesc']


    if resultCode == 0:
        callbackMetadata = stkcallback['CallbackMetadata']
        item = callbackMetadata['Item']
        for i in item:
            if i['Name'] == 'Amount':
                Amount = i['Value']
                print(Amount)
            elif i['Name'] == 'MpesaReceiptNumber':
                MpesaReceiptNumber = i['Value']
            elif i['Name'] == 'TransactionDate':
                TransactionDate = i['Value']
            elif i['Name'] == 'PhoneNumber':
                PhoneNumber = i['Value']
        receiptNumber = MpesaReceiptNumber
        amount = Amount
        transactionDate = timeConverter(str(TransactionDate))
        phoneNumber = PhoneNumber

        # add payment

        successPay = Payments(MerchantRequestID=MerchantRequestID, resultCode=resultCode,resultDesc=resultDesc,receiptNumber=receiptNumber,amount=amount,transactionDate=transactionDate,phoneNumber=phoneNumber)
        successPay.save()
        # add to Payments table, MerchantRequestID, resultCode, resultDesc, receiptNumber, amount, transactionDate, phoneNumber

        return Response('success')
    else:


        if resultCode == 1037:
            resultDesc="Timeout. User Cannot Be Reached."
        elif resultCode == 1032:
            resultDesc="Request Cancelled."
        elif resultCode == 1019:
            resultDesc="Request Expired. Try Again."
        elif resultCode == 2001:
            resultDesc="Make Sure Your Phone Number is M-Pesa Registered. You Can Edit Number in Profile."
        elif resultCode == 1001:
            resultDesc="Try Again After 2-3 Minutes."
        elif resultCode == 1:
            resultDesc="Insufficient Funds."
        else:
            # system error email admin resultDesc
            resultDesc="Error! Try Again."

        unsuccessfulPay = Payments(MerchantRequestID=MerchantRequestID, resultCode=resultCode,resultDesc=resultDesc)
        unsuccessfulPay.save()

        print('unsuccessful payment')
        return Response(resultDesc)

    # if resultCode == 0, then payment was successful
    # on successful pay, what is sent to your callbackurl is: and ResultCode=0
    # {"Body":
    #  {"stkCallback":
    #   {"MerchantRequestID":"98358-32664279-1",
    #    "CheckoutRequestID":"ws_CO_13102022154520280706803305",
    #    "ResultCode":0,
    #    "ResultDesc":"The service request is processed successfully.",
    #    "CallbackMetadata":
    #        {"Item":
    #          [
    #            {"Name":"Amount","Value":1.00},
    #            {"Name":"MpesaReceiptNumber","Value":"QJD4T7ZOT0"},
    #            {"Name":"Balance"},
    #            {"Name":"TransactionDate","Value":20221013154544},
    #            {"Name":"PhoneNumber","Value":254706803305}
    #          ]
    #        }
    #   }
    #  }
    # }

    # on time out, and ResultCode == 1037
    # {"Body":
    #   {"stkCallback":
    #     {"MerchantRequestID":"98357-32706531-1",
    #      "CheckoutRequestID":"ws_CO_13102022155941641714596833",
    #      "ResultCode":1037,
    #      "ResultDesc":"DS timeout user cannot be reached"
    #      }
    #    }
    # }

    # if cancelled by user ResultCode == 1032
    # {"Body":{"stkCallback":{"MerchantRequestID":"98371-32721597-1","CheckoutRequestID":"ws_CO_13102022160444963706803305","ResultCode":1032,"ResultDesc":"Request cancelled by user"}}}
    # Transaction has expired resultcode == 1019
    # {'Body': {'stkCallback': {'MerchantRequestID': '68425-53956289-1', 'CheckoutRequestID': 'ws_CO_24102022151123731706803305', 'ResultCode': 1019, 'ResultDesc': 'Transaction has expired'}}}
    #  if user enters wrong pin ResultCode == 2001
    # {"Body":{"stkCallback":{"MerchantRequestID":"20561-30631158-1","CheckoutRequestID":"ws_CO_13102022160809538706803305","ResultCode":2001,"ResultDesc":"The initiator information is invalid."}}}
    # if user not m-pesa registered
    # {"Body":{"stkCallback":{"MerchantRequestID":"120570-20495815-1","CheckoutRequestID":"ws_CO_13102022164603749736005983","ResultCode":2001,"ResultDesc":"The initiator information is invalid."}}}

@api_view(['POST'])
def checkPayment(request):
    data = request.data
    MerchantRequestID = literal_eval(data['MerchantRequestID'])
    # through MerchantRequestID we can check for the status of payment in payment table
    # and return a message
    if Payments.objects.filter(MerchantRequestID=MerchantRequestID).exists():
        # Daraja has sent a response
        # resultCode = 0  -> success
        #              1037 -> timeout
        #              1019 -> expired
        #              1032 -> user cancelled request
        #              2001 -> Make sure number is M-Pesa reg
        theEntry = Payments.objects.get(MerchantRequestID=MerchantRequestID)
        resultCode = theEntry.resultCode
        resultDesc = theEntry.resultDesc
        if resultCode == 0:
            return Response({"entry_found":True,"resultCode":resultCode, "resultDesc":resultDesc,"receiptNumber":theEntry.receiptNumber})
        return Response({"entry_found":True,"resultCode":resultCode, "resultDesc":resultDesc})
    else:
        # Daraja has not yet sent a response
        return Response({"entry_found":False})