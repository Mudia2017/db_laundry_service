from http import server
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import *
from .models import *
from .utils import *
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from .decorators import unauthenticated_user, account_validation_check
import requests
import json
from django.contrib.auth.forms import PasswordChangeForm

from datetime import datetime
# import datetime
import pyotp


# Create your views here.

# JUST RENDERING THE FRONT OF THE WEBSITE
def homePage(request, pk):
   
    pk = pk
    context = {'pk': pk}

    return render(request, 'laundApp/homepage.html', context)


# FUNCTION TO REGISTER COMPANY
def companyRegisterationForm(request):
    try:
        serverMsg = ''
        isSuccess = False
        form = ''
        call = ''
      
        if request.method == 'POST':
            terms_condition = request.POST.get('checkbox')
            if User.objects.filter(username= request.POST.get('username')).exists():
                serverMsg = 'Username name already exist in the system!'
                form = formData(request)
                context = {'form': form, 'isSuccess': isSuccess, 'serverMsg': serverMsg, 'call': call}
                return render(request, 'laundApp/adminRegisterForm.html', context)
            elif User.objects.filter(email= request.POST.get('email')).exists():
                serverMsg = 'Email name already exist in the system!'
                form = formData(request)
                context = {'form': form, 'isSuccess': isSuccess, 'serverMsg': serverMsg, 'call': call}
                return render(request, 'laundApp/adminRegisterForm.html', context)
            elif terms_condition != 'true':
                serverMsg = 'You most agree to terms and condition!'
                form = formData(request)
                context = {'form': form, 'isSuccess': isSuccess, 'serverMsg': serverMsg, 'call': call}
                return render(request, 'laundApp/adminRegisterForm.html', context)
            else:
                form = CreateUserForm(request.POST)
                if form.is_valid():
                    if CompanyRegisterForm.objects.filter(businessName__icontains = request.POST.get('businessName')).exists():
                        serverMsg = 'Business name already exist in the system!'
                        form = formData(request)
                        context = {'form': form, 'isSuccess': isSuccess, 'serverMsg': serverMsg, 'call': call}
                        return render(request, 'laundApp/adminRegisterForm.html', context)
                    else:
                        user = form.save()
                        CompanyRegisterForm.objects.create(
                            user= user,
                            businessName = request.POST.get('businessName'),
                            mobile = formatPhoneNO(request.POST.get('mobile'), request.POST.get('mobile_code')),
                            phone = formatPhoneNO(request.POST.get('phone'), request.POST.get('phone_code')),
                            streetAddress1 = request.POST.get('streetAddress1'),
                            streetAddress2 = request.POST.get('streetAddress2'),
                            city = request.POST.get('city'),
                            state = request.POST.get('state'),
                            postal = request.POST.get('postal'),
                            country = request.POST.get('country'),
                            businessId = generateRandomId(request),
                            discoverUs = request.POST.get('discoverUs'),
                            others = request.POST.get('others'),
                            termsCondition = convertToBoolean(terms_condition),
                        )

                        # SEND OTP CODE TO VERIFY PHONE NUMBER BEFORE COMPLETING REGISTRATION PROCESS
                        send_otp(request)
                        
                        return redirect('otp', 'frmRegister')
                    
                else:
                    serverMsg = form.error_messages
                    form = formData(request)
        else:
            form = ''
    except Exception as e:
        if CompanyRegisterForm.objects.filter(businessName__icontains = request.POST.get('businessName')).exists():
            call = 'companyCreated'
            serverMsg = 'Account was created successfully. OTP code could not be sent to the mobile number provided. Kindly confirm to re-generate OTP'
        else:
            
            serverMsg = 'The server could not accept your request because it was not valid. Please try again and if the error keeps happening get in contact with us.'
        form = formData(request)
    context = {'form': form, 'serverMsg': serverMsg, 'isSuccess': isSuccess, 'call': call}

    return render(request, 'laundApp/adminRegisterForm.html', context)


# FUNCTION TO RE-GENERATE OTP
@unauthenticated_user
def re_generate_otp(request, call):
    serverMsg = ''
    isSuccess = False

    try:
        if request.session['businessId'] is not None:
            companyProfile = CompanyRegisterForm.objects.get(businessId= request.session['businessId'])
            if companyProfile.otpConfirm:
                isSuccess = True
                serverMsg = 'OTP have been confirmed. Proceed to the dashboard'
            else:
                send_otp(request)
                if call == 'frmProfile':
                    return redirect('otp_frm_profile')
                elif call == 'frmRegister':
                    return redirect('otp')
    except Exception as e:
        serverMsg = 'Could not verify your phone number. Ensure you provide the country code before the number and try again.'

    context = {'isSuccess': isSuccess, 'serverMsg': serverMsg}
    return render(request, 'laundApp/otp.html', context)


# THIS OTP WILL BE CALLED WHEN USER UPDATE THEIR PROFILE
@unauthenticated_user
def otpFrmProfile(request):
    isSuccess = False
    serverMsg = ''
    try:
        if request.method == 'POST':
            otp = request.POST['otp']
            otp_secret_key = request.session['otp_secret_key']
            otp_valid_date = request.session['otp_valid_date']
            businessId = request.session['businessId']

            if otp_secret_key and otp_valid_date is not None:
                valid_until = datetime.fromisoformat(otp_valid_date)

                if valid_until > datetime.now():
                    totp = pyotp.TOTP(otp_secret_key, interval=120)
                    if totp.verify(otp):
                        # UPDATE THE DATABASE TABLE THAT ACCT HAVE BEEN VIERIFIED THROUGH OTP
                        # FOR REAL TIME UPDATE, UPDATE OTP REQUEST SESSION.
                        # DELETE THE OTP RECORD WE SAVED IN THE REQUEST SESSION
                        # REDIRECT TO THE PROFILE PAGE...
                        companyProfile = CompanyRegisterForm.objects.get(businessId= businessId)
                        companyProfile.otpConfirm = True
                        companyProfile.save()
                        request.session['otpConfirm'] = companyProfile.otpConfirm

                        del request.session['otp_secret_key']
                        del request.session['otp_valid_date']
                        del request.session['otp_code']
                        
                        request.session['isSuccess'] = True
                        return redirect('profile')
                    else:
                        serverMsg = 'invalid one time password'
                else:
                    serverMsg = 'one time password has expired'
            else:
                serverMsg = 'ups...something went wrong'
        else:
            pass
    except Exception as e:
        serverMsg = e.args
    context = {'isSuccess': isSuccess, 'serverMsg': serverMsg}
    return render(request, 'laundApp/otpFrmProfile.html', context)


# FUNCTION TO DISPLAY OTP AND VALIDATE OTP CODE SUPPLIED BY THE USER
def otp_view(request):
    isSuccess = False
    serverMsg = ''
    if request.method == 'POST':
        try:
            otp = request.POST['otp']
            otp_secret_key = request.session['otp_secret_key']
            otp_valid_date = request.session['otp_valid_date']
            businessId = request.session['businessId']

            if otp_secret_key and otp_valid_date is not None:
                valid_until = datetime.fromisoformat(otp_valid_date)

                if valid_until > datetime.now():
                    totp = pyotp.TOTP(otp_secret_key, interval=120)
                    if totp.verify(otp):
                        
                        # UPDATE THE DATABASE TABLE THAT ACCT HAVE BEEN VIERIFIED THROUGH OTP
                        # DELETE THE OTP RECORD WE SAVED IN THE REQUEST SESSION
                        # REDIRECT TO THE LOGIN PAGE...
                        companyProfile = CompanyRegisterForm.objects.get(businessId= businessId)
                        companyProfile.otpConfirm = True
                        companyProfile.save()
                        del request.session['otp_secret_key']
                        del request.session['otp_valid_date']
                        del request.session['businessId']
                        del request.session['mobile']
                        del request.session['otp_code']
                        
                        return redirect('login')
                    else:
                        serverMsg = 'invalid one time password'
                else:
                    serverMsg = 'one time password has expired'
            else:
                serverMsg = 'ups...something went wrong'
        except Exception as e:
            serverMsg = e.args
    else:
        isSuccess = True
        serverMsg = 'Enter the OTP code sent to your mobile number.'
    context = {'isSuccess': isSuccess, 'serverMsg': serverMsg}
    return render(request, 'laundApp/otp.html', context)



def loginPage(request):
    serverMsg = ''
    isSuccess = False
    
    try:
        if request.method == 'POST':
            credential = request.POST.get('email').strip()
            password = request.POST.get('password')
            
            # CHECKING IF EMAIL WAS USED AS LOGIN DETAIL
            if '@' in credential:
                credential = User.objects.get(email=credential)
                user = authenticate(request, username=credential, password=password)

                if user is not None:
                    login(request, user)
                    companyProfile = CompanyRegisterForm.objects.get(user= user.id)
                    saveCompanyProfileInfoToRequestSession(request, companyProfile)
                    companyProfile.lastLogin = datetime.now()
                    companyProfile.save()
                    return redirect('dashboard')
                else:
                    serverMsg = 'Username or password is incorrect'
            elif credential:
                user = authenticate(request, username=credential, password=password)

                if user is not None:
                    login(request, user)
                    companyProfile = CompanyRegisterForm.objects.get(user= user.id)
                    saveCompanyProfileInfoToRequestSession(request, companyProfile)
                    companyProfile.lastLogin = datetime.now()
                    companyProfile.save()
                    return redirect('dashboard')
                
                else:
                    serverMsg = 'Username or password is incorrect'
            else:
                serverMsg = 'Username or password is incorrect'
        else:
            pass
            # IF A ACTIVE USER TRY TO MANIPULATE 'IF STATEMENT' ON THE HTML BY DISABLING THE LOGIN BUTTON,
            # THIS ELSE STATEMENT WILL RE-DIRECT THEM TO HOME PAGE
            # isAuthenticated = False
            # isAuthenticated = request.user.is_authenticated
            # if isAuthenticated:
            #     return redirect('homePage')
        
    except Exception as e:
        serverMsg = e.args[0]
    context = {'isSuccess': isSuccess, 'serverMsg': serverMsg}
    return render(request, 'laundApp/login.html', context)


@unauthenticated_user
def logoutUser(request):
    logout(request)
    pk = '0'
    return redirect('homePage', pk)


# COMPANY DASH BOARD
@unauthenticated_user
def dashBoard(request):

    isSuccess = True
    serverMsg = 'Successful'
    context = {'isSuccess': isSuccess, 'serverMsg': serverMsg, 'showMenu': 'Dashbash'}


    return render(request, 'laundApp/dash_board.html', context)


# COMPANY SERVICE PAGE OVERVIEW
@unauthenticated_user
@account_validation_check
def services(request):

    isSuccess = False
    serverMsg = ''
    serviceForm = ''
    isTransparentTemplate = False
    serviceList = ''
    format = []
    catList = ''
   
    try:
        if request.method == 'POST':
            if request.POST.get('proceedBtn') == 'Proceed' and request.POST.get('action') != '':
                selected_values = request.POST.getlist('chkBox')
                if request.POST.get('action') == 'active':
                    for select in selected_values:
                        rec = Services.objects.get(id= select, comProfileField__businessId__exact = request.session['businessId'])
                        rec.active = True
                        rec.updatedDate = datetime.today()
                        rec.updatedBy = request.user.id
                        rec.save()
                    request.session['isSuccess'] = True
                    return redirect('serviceList')
                elif request.POST.get('action') == 'inactive':
                    for select in selected_values:
                        rec = Services.objects.get(id= select, comProfileField__businessId__exact = request.session['businessId'])
                        rec.active = False
                        rec.updatedDate = datetime.today()
                        rec.updatedBy = request.user.id
                        rec.save()
                    request.session['isSuccess'] = True
                    return redirect('serviceList')
               
                # DELETE IS HANDLED FROM JAVA SCRIPT
                else:
                    serverMsg = 'No action was selected'
        else:
            serviceList = Services.objects.filter(comProfileField__businessId__exact= request.session['businessId'])
            catList = Category.objects.filter(comProfileField__businessId= request.session['businessId'])
            if request.session['isSuccess'] == True:
                isSuccess = True
                request.session['isSuccess'] = False

            if request.session['isTransparentTemplate'] == True:
                isTransparentTemplate = True
                request.session['isTransparentTemplate'] = False
            
            if request.session['serverMsg'] != '':
                serverMsg = request.session['serverMsg'] 
                request.session['serverMsg'] = ''

        # === WORK IN PROGRESS... SEARCH RECORD FIELD ======
            format = getJsonFormatList(serviceList)
            
            format = json.dumps(format)
        # =============== WORK IN PROGRESS ====================
    except Exception as e:
        serviceList = Services.objects.filter(comProfileField__businessId__exact= request.session['businessId']).order_by('-id').reverse()
        catList = Category.objects.filter(comProfileField__businessId= request.session['businessId'])
        serverMsg = e.args
    context = {
        'serviceForm': serviceForm, 
        'isSuccess': isSuccess, 'serverMsg': serverMsg, 
        'showMenu': 'List of Services', 
        'isTransparentTemplate': isTransparentTemplate,
        'serviceList': serviceList,
        'format': format,
        'catList': catList
        }


    return render(request, 'laundApp/services/services.html', context)


def viewServiceList(request):
   
    return redirect ('services')
 


# WE USE THIS FUNCTION TO GET SERVICE RECORD TO THE UPDATE FORM
@unauthenticated_user
@account_validation_check
def saveService(request):
    jrecord = ''
    
    try:
        if request.method == 'POST':
            jsonData = json.loads(request.body)
            
            if jsonData['call'] == 'getRec':
                record = Services.objects.get(id= jsonData['id'])
                jrecord = getServiceInJsonFormat(record)
            elif jsonData['call'] == 'del':
                selectedList = jsonData['selectedList']
                for select in selectedList:
                    rec = Services.objects.get(id= select, comProfileField__businessId__exact = request.session['businessId'])
                    rec.delete()
                request.session['isSuccess'] = True
                jrecord = 'successful'
            elif jsonData['call'] == 'saveServiceReq':

                if Services.objects.filter(serviceName__iexact= jsonData['serviceName'], comProfileField__businessId__exact = request.session['businessId']).exists():
                    request.session['serverMsg'] = 'Service name already exist in the system.'
                    request.session['isTransparentTemplate'] = True
                    jrecord = jsonData
                else:
                    comProfile = CompanyRegisterForm.objects.get(businessId= request.session['businessId'])
                    category = Category.objects.get(id= jsonData['cat_id'])
                    service_form = ServiceFormField(jsonData)
                    if service_form.is_valid():
                        Services.objects.create(
                            comProfileField= comProfile,
                            serviceName= jsonData['serviceName'],
                            categoryId= category,
                            ironNormal= jsonData['ironNormal'],
                            ironFast= jsonData['ironFast'],
                            laundryNormal= jsonData['laundryNormal'],
                            laundryFast= jsonData['laundryFast'],
                            laundryIronNormal= jsonData['laundryIronNormal'],
                            laundryIronFast= jsonData['laundryIronFast'],
                            dryWashNormal= jsonData['dryWashNormal'],
                            dryWashFast= jsonData['dryWashFast'],
                            stainRemoval= jsonData['stainRemoval'],
                            dryUp= jsonData['dryUp'],
                            others= jsonData['others'],
                            iconId= jsonData['iconId'],
                            createdBy= request.user.id,
                            active= jsonData['activeSwitchBtn']
                        )
                        request.session['isSuccess'] = True
                        jrecord = 'success'
                        return JsonResponse(jrecord, safe=False)
                    else:
                        request.session['serverMsg'] = 'Record not valid!'
            elif jsonData['call'] == 'updateServiceReq':
                count = Services.objects.filter(serviceName__iexact= jsonData['serviceName'], comProfileField__businessId__exact = request.session['businessId']).count()
                if count > 1:    
                    request.session['serverMsg'] = 'Fail to update. Service name already exist in the system.'
                    
                else:
                    serviceRecord = Services.objects.get(id= jsonData['id'])
                    category = Category.objects.get(id= jsonData['cat_id'])
                    serviceRecUpdate = ServiceFormField(jsonData, instance=serviceRecord)
                    if serviceRecUpdate.is_valid():
                        serviceRecUpdate.save()
                        serviceRecord.updatedDate = datetime.now()
                        serviceRecord.updatedBy = request.user.id
                        serviceRecord.active = jsonData['activeSwitchBtn']
                        serviceRecord.categoryId = category
                        serviceRecord.save()
                        
                        request.session['isSuccess'] = True
                        jrecord = 'success'
                        return JsonResponse(jrecord, safe=False)
                    else:
                        request.session['serverMsg'] = 'Fail to update. Record not valid!!!'
                        request.session['isTransparentTemplate'] = True
                        jrecord = jsonData
              
    except Exception as e:
        request.session['serverMsg'] = e.args
    
    return JsonResponse(json.dumps(jrecord), safe=False)



@unauthenticated_user
@account_validation_check
def settings(request):
    isSuccess = False
    serverMsg = ''
    catList = ''

    try:
        if request.method == 'POST':
            pass 

        else:
            catList = Category.objects.filter(comProfileField__businessId__exact= request.session['businessId'])
            
            if request.session['isSuccess'] == True:
                isSuccess = True
                request.session['isSuccess'] = False

            elif request.session['isSuccess'] == False and request.session['serverMsg'] != '':
                serverMsg = request.session['serverMsg'] 
                request.session['serverMsg'] = ''
    except Exception as e:
        serverMsg = e.args

    context = {
        'isSuccess': isSuccess, 'serverMsg': serverMsg, 
        'showMenu': 'Settings', 'catList': catList,
        
    }

    return render(request, 'laundApp/settings.html', context)


# SAVE REQUEST FOR SETTINGS
# @account_validation_check
@unauthenticated_user
def saveSettings(request):
    jrecord = ''
    checkDoubleRec = ''
    count = 0
    
    try:

        if request.method == 'POST':
            jsonData = json.loads(request.body)
            comProfile = CompanyRegisterForm.objects.get(businessId= request.session['businessId'])
            if jsonData['call'] == 'saveCat':
                if not jsonData['catName'] == '':
                    if not Category.objects.filter(comProfileField__businessId= request.session['businessId'], catName= jsonData['catName']).exists():
                        Category.objects.create(
                            comProfileField= comProfile,
                            catName= jsonData['catName'],
                            updatedBy= request.user.id,
                            active= jsonData['active']
                        )

                        request.session['isSuccess'] = True
                        jrecord = 'success'
                        return JsonResponse(jrecord, safe=False)
                    else:
                        request.session['serverMsg'] = 'Category name already exist in the system'
                else:
                    request.session['serverMsg'] = 'Category name was not given!'
            elif jsonData['call'] == 'updateCat':
                category = Category.objects.get(id= jsonData['catId'], comProfileField__businessId= request.session['businessId'])
                if not jsonData['catName'] == '':
                    checkDoubleRec = Category.objects.filter(comProfileField__businessId= request.session['businessId'], catName__iexact= jsonData['catName'])
                    for doubleRecCheck in checkDoubleRec:
                        if doubleRecCheck.id != category.id:
                            count += 1
                    if count > 0:
                        request.session['serverMsg'] = 'Category name provided already exist in the system.'
                        
                    else:
                        category.catName = jsonData['catName']
                        category.updatedBy = request.user.id
                        category.updatedDate = datetime.now()
                        category.active = jsonData['active']
                        category.save()

                        request.session['isSuccess'] = True
                        jrecord = 'success'
                        return JsonResponse(jrecord, safe=False)
                else:
                    request.session['serverMsg'] = 'Category name was not given!'
    except Exception as e:
        request.session['serverMsg'] = e.args

    return JsonResponse(json.dumps(jrecord), safe=False)


@unauthenticated_user
def profile(request):
    comDetail = ''
    serverMsg = ''
    isSuccess = False
    isOTP = False
    try:
        if request.method == 'POST':
            pass
        else:
            comDetail = CompanyRegisterForm.objects.get(businessId= request.session['businessId'])

            if request.session['isSuccess'] == True:
                isSuccess = True
                request.session['isSuccess'] = False
            elif request.session['serverMsg'] != '':
                serverMsg = request.session['serverMsg'] 
                request.session['serverMsg'] = ''
            
            if not comDetail.otpConfirm:
                isOTP = True
    except Exception as e:
        serverMsg = e.args

    context = {
        'showMenu': 'My Profile',
        'comDetail': comDetail,
        'serverMsg': serverMsg,
        'isSuccess': isSuccess,
        'isOTP': isOTP
    }

    return render(request, 'laundApp/profile.html', context)


# UPDATE/SAVE PROFILE INFORMATION
@unauthenticated_user
def saveUpdateProfile(request):
    jrecord = ''

    try:
        if request.method == 'POST':
            jsonData = json.loads(request.body)
            if jsonData['call'] == 'updateDetailProfile':
                valid_fields = UpdateComProfile(jsonData)
                if valid_fields.is_valid():
                    if not jsonData['businessName'] == '':
                        comProfile = CompanyRegisterForm.objects.get(businessId= request.session['businessId'])
                        comProfile.businessName = jsonData['businessName']
                        comProfile.mobile = formatPhoneNO(jsonData['mobile'], jsonData['mobile_code'])
                        comProfile.phone = formatPhoneNO(jsonData['phone'], jsonData['phone_code'])
                        comProfile.streetAddress1 = jsonData['streetAddress1']
                        comProfile.streetAddress2 = jsonData['streetAddress2']
                        comProfile.city = jsonData['city']
                        comProfile.state = jsonData['state']
                        comProfile.postal = jsonData['postal']
                        comProfile.country = jsonData['country']
                        comProfile.active = jsonData['active']
                        comProfile.otpConfirm = False
                        comProfile.save()

                        request.session['isSuccess'] = True
                        request.session['otpConfirm'] = comProfile.otpConfirm
                        request.session['businessName'] = jsonData['businessName']
                        request.session['active'] = jsonData['active']
                        jrecord = 'success'
                        return JsonResponse(jrecord, safe=False)
                    else:
                        request.session['serverMsg'] = 'Company name must not be empty!'
                else:
                    request.session['serverMsg'] = 'Record not valid!'
            elif jsonData['call'] == 'reset_pwd':
                form = PasswordChangeForm(data=jsonData, user=request.user)
                if form.is_valid():
                    user = form.save()
                    update_session_auth_hash(request, user)  # Important! Otherwise the user’s auth session will be invalidated and she/he will have to log in again.
                    request.session['isSuccess'] = True
                    jrecord = 'success'
                else:
                    request.session['serverMsg'] = 'Password is not valid. New password must contain at least 8 characters. Both numeric and alphabet'
    except Exception as e:
        jrecord = e.args

    return JsonResponse(jrecord, safe=False)


def loadBooking(request):
    serverMsg = ''
    isSuccess = False
    categories = ''
    services = ''

    categories = Category.objects.filter(comProfileField__businessId= request.session['businessId'], active= True)
    services = Services.objects.filter(comProfileField__businessId= request.session['businessId'], categoryId__active= True, active= True)
    services = json.dumps( getJsonFormatList(services) )
    context = {'showMenu': 'Booking',
        'serverMsg': serverMsg,
        'isSuccess': isSuccess,
        'categories': categories,
        'services': services
        }

    return render(request, 'laundApp/booking.html', context)

# def sendSMS():

#     url = "https://telesign-telesign-send-sms-verification-code-v1.p.rapidapi.com/sms-verification-code"
   

#     querystring = {"phoneNumber":"2348187709332","verifyCode":"8821","appName":"LaundApp"}

#     headers = {
#         "X-RapidAPI-Key": "2378aa7550msh4ab82aec11f8618p156cd1jsnf3e0c409f9b8",
#         "X-RapidAPI-Host": "telesign-telesign-send-sms-verification-code-v1.p.rapidapi.com"
#     }

#     response = requests.request("POST", url, headers=headers, params=querystring)

#     print(response.text)