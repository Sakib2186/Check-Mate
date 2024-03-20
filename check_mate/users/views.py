from django.shortcuts import render,HttpResponse,redirect,reverse
import logging
from datetime import datetime
import traceback
from django.contrib.auth.models import auth,User
from django.contrib import messages
from system_administrator.models import *
from system_administrator.system_error_handling import ErrorHandling
from .render_data import Login
from .models import *
import pyotp
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required


logger=logging.getLogger(__name__)

# Create your views here.

def check_mate(request):
    return HttpResponse("Landing Page")
def login(request):

    try:

        if request.method == "POST":

            if request.POST.get('login_button_pressed'):
                #when user presses login in button fetching the data he gave

                user_username = request.POST.get('user_username')
                user_password = request.POST.get('user_password')
                
                #getting user credentials from django users model
                #it would be valid for both admin/superuser and normal users of system
                user = auth.authenticate(username=user_username,password=user_password)
                #if user not found then logged him in
                if user is not None:
                    
                    try:
                        school_user = School_Users.objects.get(user_id = user_username)
                        #checking to see if school user is verified or not
                        if school_user.user_otp_verified:
                            auth.login(request,user)
                            return redirect('users:dashboard')
                        else:
                            #not verified so sending them the link for verification
                            verification_link = reverse('users:registration_email_verification', args=[school_user.user_id])
                            verification_url = request.build_absolute_uri(verification_link)
                            verification_message = f"Your account is not verified yet! Verification link: <a href='{verification_url}'>{verification_url}</a>"
                            messages.error(request, mark_safe(verification_message))
                            return redirect('users:login') 
                    except:
                        #admin is logging in
                        auth.login(request,user)
                        return redirect('users:dashboard')
                else:
                    #user might not be registered or gives the wrong credentials
                    messages.info(request,"Credentials given are wrong")
                    return redirect('users:login') 

        context = {
            'page_title':"Check Mate"
        }
        
        return render(request,"login_page.html",context)
    
    except Exception as e:
        #saving error information in database if error occured
        logger.error("An error occurred for during logging in at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.save_system_errors('Login Error',error_name=e,error_traceback=traceback.format_exc())
        return HttpResponse("Bad Request")
    
def registration(request):

    try:

        if request.method == "POST":

            if request.POST.get('registration_button'):
                
                #getting user credentials
                user_name = request.POST.get('user_name')
                password = request.POST.get('user_password')
                confirm_password = request.POST.get('confirm_user_password')

                #getting maipulated data from render_data
                registration = Login.register_user(request,user_name,password,confirm_password)
                #checking to see if user is successfully registered
                if registration[0]:
                    return redirect('users:registration_email_verification',registration[1].user_id)
                else:
                    messages.error(request,registration[1])
                    return redirect('users:registration')

        context = {
            'page_title':'Check Mate'
        }

        return render(request,"registration.html",context)

    except Exception as e:
        #saving error information in database if error occured
        logger.error("An error occurred for during logging in at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.save_system_errors('Registration Error',error_name=e,error_traceback=traceback.format_exc())
        return HttpResponse("Bad Request")

def registration_email_verification(request,user_id):

    try:

        school_user = School_Users.objects.get(user_id = user_id)
        #if user is not verified then allowing to enter page
        if not school_user.user_otp_verified:

            if request.method == "POST":

                if request.POST.get('submit_otp'):
                    
                    #getting user otp
                    otp = str(request.POST.get('otp'))
                    
                    #checking if otp is empty
                    if otp == "":
                        messages.error(request,'Provide OTP!')
                        return redirect('users:registration_email_verification',user_id)
                    try:
                        #putting them session dictionary
                        otp_secret_key = request.session['otp_secret_key']
                        otp_valid_date = request.session['otp_valid_date']
                        print("here")
                        #checking to see if otp is valid and matches with users input one
                        if otp_secret_key and otp_valid_date is not None:
                            valid_until = datetime.fromisoformat(otp_valid_date)

                            if valid_until > datetime.now():
                                totp = pyotp.TOTP(otp_secret_key,interval = 60)
                                print("here2")
                                if totp.verify(otp):
                                    user = User.objects.get(username = user_id)
                                    school_user.user_otp_verified = True
                                    school_user.save()
                                    auth.login(request,user)
                                    #removing the otp keys from the session
                                    request.session.pop('otp_secret_key', None)
                                    request.session.pop('otp_valid_date', None)
                                    return redirect('users:dashboard')
                                else:
                                    messages.error(request,"invalid OTP")
                                    return redirect('users:registration_email_verification',user_id)
                            else:
                                messages.error(request,"OTP expired")
                                redirect('users:registration_email_verification',user_id)

                        else:
                            messages.error(request,"Something went wrong..")
                            redirect('users:registration_email_verification',user_id)
                    except:
                        messages.error(request,"invalid OTP")
                        return redirect('users:registration_email_verification',user_id)

                if request.POST.get('resend_otp'):
                    
                    request.session.pop('otp_secret_key', None)
                    request.session.pop('otp_valid_date', None)
                    Login.registration_email(request,school_user)
                    redirect('users:registration_email_verification',user_id)
                    
            context = {
                'page_title':'Check Mate'
            }
            return render(request,"registration_verification.html",context)
        
        else:
            return HttpResponse("Already verified")

    except Exception as e:
        #saving error information in database if error occured
        logger.error("An error occurred for during logging in at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.save_system_errors('Registration Error',error_name=e,error_traceback=traceback.format_exc())
        return HttpResponse("Bad Request")

@login_required
def dashboard(request):

    try:
        if request.user.is_superuser:
            print("YOO")
        else:
            print("normal")
        context = {
            'page_title':'Check Mate',
        }

        return render(request,"dashboard.html",context)

    except Exception as e:
        #saving error information in database if error occured
        logger.error("An error occurred for during logging in at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.save_system_errors('Registration Error',error_name=e,error_traceback=traceback.format_exc())
        return HttpResponse("Bad Request")
    
@login_required
def logout(request):
    
    try:
        auth.logout(request)
        return redirect('users:login')
    except Exception as e:
        #saving error information in database if error occured
        logger.error("An error occurred for during logging in at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.save_system_errors('Registration Error',error_name=e,error_traceback=traceback.format_exc())
        return HttpResponse("Bad Request")
