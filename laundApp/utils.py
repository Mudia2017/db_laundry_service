from operator import truediv
import uuid
import pyotp
from datetime import datetime, timedelta
from twilio.rest import Client
import re
from . models import CompanyRegisterForm
from decouple import config


# USED TO GENERATE RANDOM BUSINESS ID
def generateRandomId(request):
    randamId = str(uuid.uuid4().time_low)[:6]
    prefix = request.POST.get('prefix')
    randamId = prefix.upper() + randamId
    # USED TO GET COMPANY PROFILE WHEN OTP IS CONFIRMED
    # UPDATE OTP STATUS AND DELETE THE SESSION
    request.session['businessId'] = str(randamId) 
    return randamId


# FORMAT PHONE NUMBER TO INTERNATIONAL STANDARD (WITH COUNTRY CODE)
def formatPhoneNO(phoneNo, countryCode):
    if phoneNo and countryCode is not None:
        # REGEX PATTERN FOR REMOVING LEADING ZEROS FROM AN INPUT STRING
        regexPattern = "^0+(?!$)"
        # REPLACE THE MATCHED REGEX PATTERN WITH AN EMPTY STRING
        outputString = re.sub(regexPattern, '', phoneNo)
        # RETURNING OUTPUT STRING AFTER REMOVING LEADING 0s
        print(countryCode + outputString)
        return countryCode + outputString
    return ''

# CONVERT TO BOOLEAN FIELD 
def convertToBoolean(val):
    if val == 'true':
        val = True
    else:
        val = False
    return val


# === COMPANY FORM REGISTRATION INPUT ====
# == IF THE PROCESSING OF REGISTING THE COMPANY FAIL, 
#  THIS WILL HELP THE RETAIN THE RECORDS ON THE TEMPLATE
def formData(request):
    form = {
        'first_name': request.POST.get('first_name'),
        'last_name': request.POST.get('last_name'),
        'username': request.POST.get('username'),
        'prefix': request.POST.get('prefix'),
        'businessName': request.POST.get('businessName'),
        'email': request.POST.get('email'),
        'mobile': request.POST.get('mobile'),
        'phone': request.POST.get('phone'),
        'streetAddress1': request.POST.get('streetAddress1'),
        'streetAddress2': request.POST.get('streetAddress2'),
        'city': request.POST.get('city'),
        'state': request.POST.get('state'),
        'postal': request.POST.get('postal'),
        'country': request.POST.get('country'),
        # 'discoverUs': request.POST.get('discoverUs'),
        'others': request.POST.get('others'),
    }
    return form


# FUNCTION USED TO SEND OTP CODE TO USERS
def send_otp(request):
    totp = pyotp.TOTP(pyotp.random_base32(), interval=120)
    otp = totp.now()
    # LET'S STORE THE KEY IN THE USER SESSION
    request.session['otp_secret_key'] = totp.secret
    # ADD 2 MINS TO THE CURRENT TIME AND STORE IN USER SESSION
    valid_date = datetime.now() + timedelta(minutes=2)
    request.session['otp_valid_date'] = str(valid_date)
    request.session['otp_code'] = otp

    if request.method == 'POST':
        # WE SAVE THE MOBILE NUMBER IN REQUEST SESSION IN CASE THE USER RE-GENERATE OTP
        request.session['mobile'] = formatPhoneNO (request.POST.get("mobile"), request.POST.get("mobile_code"))

    # SEND THE SECRET OTP VIA SMS TO THE PHONE NUMBER PROVIDED
    if request.POST.get('mobile') is not None:
        telNumber = formatPhoneNO (request.POST.get("mobile"), request.POST.get("mobile_code"))
        sendTextMsg(telNumber, f"Your one time code is {otp}")
        
        # THIS BLOCK IS EXECUTED IF THE USER RE-GENERATE OTP CODE
    elif 'mobile' in request.session:
    # elif request.session['mobile'] is not None:
        telNumber = str (request.session['mobile'])
        sendTextMsg(telNumber, f"Your one time code is {otp}")

        # IN CASES WHERE UPDATE WAS CARRIED OUT ON THE COMPANY 
        # PROFILE ACCT, GET THE CURRENT MOBILE NO PROVIEDED AND 
        # AND SEND OPT 
    else:
        profile = CompanyRegisterForm.objects.get(businessId= request.session['businessId'])
        sendTextMsg(profile.mobile, f"Your one time code is {otp}")
    print(f"Your one time password is {otp}")
    

# EXTENDED FUNCTION TO SEND OTP CODE TO PHONE NUMBER PROVIDED
# THIS CODE IS FROM 3RD PARTY SERVICE PROVIDER (TWILIO) 
# THEY HELP US SEND OTP CODE VIA SMS OF PHONE NUMBER REGISTERED (SINCE IT'S A TRIAL VERSION)
def sendTextMsg(receiverNo:str, body:str):
    account_sid = config('TWILIO_ACCOUNT_SID')
    auth_token = config('TWILIO_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    body=body,
    from_="+15076876623",
    to=receiverNo
    )
    print(message.sid)


# THIS FUNCTION IS USED TO SAVE COMPANY PROFILE INFO ON 
# REQUEST SESSION ONCE LOGIN IS SUCCESSFUL
def saveCompanyProfileInfoToRequestSession(request, companyProfile):
    request.session['businessId'] = companyProfile.businessId
    request.session['businessName'] = companyProfile.businessName
    request.session['active'] = companyProfile.active
    request.session['acctLevel'] = companyProfile.acctLevel
    request.session['otpConfirm'] = companyProfile.otpConfirm
    request.session['termsCondition'] = companyProfile.termsCondition

    # LOGICAL OPERATIONS INCLUDE...
    request.session['isSuccess'] = False
    request.session['isTransparentTemplate'] = False
    request.session['serverMsg'] = ''


# FINAL CHECK FOR COMPANY TO KNOW IF ALL CONDITIONS HAVE BEEN MEANT
# THIS IS DONE WHEN EVER THEY LOGIN



#  THIS WILL HELP THE RETAIN THE RECORDS ON THE TEMPLATE (ADD SERVICE)
def serviceRec(request):
    form = {
        'serviceName': request.POST.get('serviceName'),
        'categoryId': request.POST.get('categoryId'),
        'ironNormal': request.POST.get('ironNormal'),
        'ironFast': request.POST.get('ironFast'),
        'laundryNormal': request.POST.get('laundryNormal'),
        'laundryFast': request.POST.get('laundryFast'),
        'laundryIronNormal': request.POST.get('laundryIronNormal'),
        'laundryIronFast': request.POST.get('laundryIronFast'),
        'dryWashNormal': request.POST.get('dryWashNormal'),
        'dryWashFast': request.POST.get('dryWashFast'),
        'stainRemoval': request.POST.get('stainRemoval'),
        'dryUp': request.POST.get('dryUp'),
        'others': request.POST.get('others'),
        
    }
    return form


# ARRANGE ITEM IN JSON FORMAT
def getServiceInJsonFormat(record):
    jrecord = {
        'id':record.id,
        # 'comProfileField': record.comProfileField,
        'cat_id': record.categoryId.id,
        'serviceName': record.serviceName,
        'ironNormal': record.ironNormal,
        'ironFast': record.ironFast,
        'laundryNormal': record.laundryNormal,
        'laundryFast': record.laundryFast,
        'laundryIronNormal': record.laundryIronNormal,
        'laundryIronFast': record.laundryIronFast,
        'dryWashNormal': record.dryWashNormal,
        'dryWashFast': record.dryWashFast,
        'stainRemoval': record.stainRemoval,
        'dryUp': record.dryUp,
        'others': record.others,
        'iconId': record.iconId,
        'active': record.active
    }
    return jrecord


def getJsonFormatList(data):
    recList = []
  
    for rec in data:
        record = {
            'id': rec.id,
            'comProfileField': rec.comProfileField.id,
            'categoryId': rec.categoryId.id,
            'serviceName': rec.serviceName,
            'ironNormal': rec.ironNormal,
            'ironFast': rec.ironFast,
            'laundryNormal': rec.laundryNormal,
            'laundryFast': rec.laundryFast,
            'laundryIronNormal': rec.laundryIronNormal,
            'laundryIronFast': rec.laundryIronFast,
            'dryWashNormal': rec.dryWashNormal,
            'dryWashFast': rec.dryWashFast,
            'stainRemoval': rec.stainRemoval,
            'dryUp': rec.dryUp,
            'others': rec.others,
            'iconId': rec.iconId,
            'active': rec.active
        }
        recList.append(record)
    return recList


# def formatServiceItm(data):
#     form = {
#         'serviceName': data['serviceName'],
#         'categoryId': data['categoryId'],
#         'ironNormal': data['ironNormal'],
#         'ironFast': data['ironFast'],
#         'laundryNormal': data['laundryNormal'],
#         'laundryFast': data['laundryFast'],
#         'laundryIronNormal': data['laundryIronNormal'],
#         'laundryIronFast': data['laundryIronFast'],
#         'dryWashNormal': data['dryWashNormal'],
#         'dryWashFast': data['dryWashFast'],
#         'stainRemoval': data['stainRemoval'],
#         'dryUp': data['dryUp'],
#         'others': data['others'],
        
#     }
#     return form