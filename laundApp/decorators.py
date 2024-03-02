from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect("login")
    return wrapper_func


def account_validation_check(func):
    def wrapper_func(request, *args, **kwargs):
        if not request.session['active']:
            request.session['serverMsg'] = 'Validation check was unsuccessful. Your account is not active!'
            return redirect('profile')
        elif not request.session['otpConfirm']:
            request.session['serverMsg'] = 'Validation check was unsuccessful. OTP was not confirmed with the mobile No provided.'
            return redirect('profile')
        elif not request.session['termsCondition']:
            request.session['serverMsg'] = 'Validation check was unsuccessful. Terms & condition was not checked during form registration.'
            return redirect('profile')
        elif request.session['businessId'] == '':
            request.session['serverMsg'] = 'Validation check was unsuccessful. No business ID!'
            return redirect('profile')
        elif request.session['businessName'] == '':
            request.session['serverMsg'] = 'Validation check was unsuccessful. No business Name!'
            return redirect('profile')
        else:
            return func(request, *args, **kwargs)
            
    return wrapper_func