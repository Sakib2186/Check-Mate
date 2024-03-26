from django.shortcuts import render,HttpResponse,redirect,reverse
import logging
from datetime import datetime
import traceback
from django.contrib.auth.models import auth,User
from django.contrib import messages
from system_administrator.models import *
from system_administrator.system_error_handling import ErrorHandling
from .render_data import *
from .models import *
import pyotp
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from check_mate import settings


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
        #loading the data to pass them in dictionary, context
        type_of_logged_in_user = Login.user_type_logged_in(request)
        logged_in_user = Login.logged_in_user(request)
        if logged_in_user == None:
            user = request.user.username
        else:
            user = logged_in_user.user_id
        context = {
            'page_title':'Check Mate',
            'user_type':type_of_logged_in_user,
            'media_url':settings.MEDIA_URL,
            'logged_in_user':logged_in_user,
            'year':datetime.now().year
        }

        return render(request,"dashboard.html",context)

    except Exception as e:
        #saving error information in database if error occured
        logger.error("An error occurred for during logging in at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.save_system_errors(user,error_name=e,error_traceback=traceback.format_exc())
        return HttpResponse("Bad Request")
    
@login_required
def logout(request):
    
    try:
        auth.logout(request)
        return redirect('users:login')
    except Exception as e:
        #saving error information in database if error occured
        logger.error("An error occurred for during logging in at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.save_system_errors('Logout',error_name=e,error_traceback=traceback.format_exc())
        return HttpResponse("Bad Request")

@login_required
def edit_profile(request):

    try:
        #loading the data to pass them in dictionary, context
        type_of_logged_in_user = Login.user_type_logged_in(request)
        logged_in_user = Login.logged_in_user(request)
        if logged_in_user == None:
            user = request.user.username
        else:
            user = logged_in_user.user_id
        context = {
            'page_title':'Check Mate',
            'user_type':type_of_logged_in_user,
            'media_url':settings.MEDIA_URL,
            'logged_in_user':logged_in_user,
            'year':datetime.now().year,
        }
        return render(request,"edit_account.html",context)

    except Exception as e:
        #saving error information in database if error occured
        logger.error("An error occurred for during logging in at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.save_system_errors(user,error_name=e,error_traceback=traceback.format_exc())
        return HttpResponse("Bad Request")
    
@login_required
def courses(request):

    try:
        #loading the data to pass them in dictionary, context
        type_of_logged_in_user = Login.user_type_logged_in(request)
        logged_in_user = Login.logged_in_user(request)
        all_courses = Load_Courses.get_user_courses(logged_in_user)

        if logged_in_user == None:
            user = request.user.username
        else:
            user = logged_in_user.user_id

        context = {
            'page_title':'Check Mate',
            'user_type':type_of_logged_in_user,
            'media_url':settings.MEDIA_URL,
            'logged_in_user':logged_in_user,
            'year':datetime.now().year,

            'all_courses':all_courses,
        }

        return render(request,"courses.html",context)


    except Exception as e:
        #saving error information in database if error occured
        logger.error("An error occurred for during logging in at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.save_system_errors(user,error_name=e,error_traceback=traceback.format_exc())
        return HttpResponse("Bad Request")
    
@login_required
def all_courses(request):

    try:
        #loading the data to pass them in dictionary, context
        type_of_logged_in_user = Login.user_type_logged_in(request)
        logged_in_user = Login.logged_in_user(request)
        all_courses = Load_Courses.get_user_courses(logged_in_user)


        if logged_in_user == None:
            user = request.user.username
        else:
            user = logged_in_user.user_id

        if logged_in_user == None:

            courses_all = Load_Courses.get_all_courses()

            context = {
                'page_title':'Check Mate',
                'user_type':type_of_logged_in_user,
                'media_url':settings.MEDIA_URL,
                'logged_in_user':logged_in_user,
                'year':datetime.now().year,

                'all_courses':all_courses,
                'courses':courses_all,

            }

            return render(request,"all_courses.html",context)
        else:
            return HttpResponse("Not Allowed")

    except Exception as e:
        #saving error information in database if error occured
        logger.error("An error occurred for during logging in at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.save_system_errors(user,error_name=e,error_traceback=traceback.format_exc())
        return HttpResponse("Bad Request")

@login_required
def add_course(request):

    try:
        #loading the data to pass them in dictionary, context
        type_of_logged_in_user = Login.user_type_logged_in(request)
        logged_in_user = Login.logged_in_user(request)

        if logged_in_user == None:
            user = request.user.username
        else:
            user = logged_in_user.user_id

        if logged_in_user == None:

            if request.method == "POST":

                if request.POST.get('save_course'):

                    course_name = request.POST.get('course_name')
                    course_code = request.POST.get('course_code')
                    course_description = request.POST.get('course_description')
                    cover_picture = request.FILES['cover_picture']
                    
                    result = Save.save_course(course_code,course_name,course_description,cover_picture,course=None)
                    if result[0]:
                        messages.success(request,'Course Added Successfully!')
                        return redirect('users:edit_course_details',result[1].pk)
                    else:
                        messages.error(request,"Something went wrong. Try again later")
                        return redirect('users:add_course')

                    
            context = {
                'page_title':'Check Mate',
                'user_type':type_of_logged_in_user,
                'media_url':settings.MEDIA_URL,
                'logged_in_user':logged_in_user,
                'year':datetime.now().year,

            }
            return render(request,"course_edit.html",context)
        else:
            return HttpResponse("Not Allowed")

    except Exception as e:
        #saving error information in database if error occured
        logger.error("An error occurred for during logging in at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.save_system_errors(user,error_name=e,error_traceback=traceback.format_exc())
        return HttpResponse("Bad Request")
    
@login_required
def edit_course_details(request,course_id):

    try:
        #loading the data to pass them in dictionary, context
        type_of_logged_in_user = Login.user_type_logged_in(request)
        logged_in_user = Login.logged_in_user(request)

        if logged_in_user == None:
            user = request.user.username
        else:
            user = logged_in_user.user_id

        if logged_in_user == None:
            course = Load_Courses.get_specific_course(course_id)

            if request.method == "POST":

                if request.POST.get('save_course'):

                    course_name = request.POST.get('course_name')
                    course_code = request.POST.get('course_code')
                    course_description = request.POST.get('course_description')
                    cover_picture = request.FILES.get('cover_picture')
                    if cover_picture == "":
                        cover_picture = None
                    result = Save.save_course(course_code,course_name,course_description,cover_picture,course)
                    if result[0]:
                        messages.success(request,'Course Updated Successfully!')
                        return redirect('users:edit_course_details',result[1].pk)
                    else:
                        messages.error(request,"Something went wrong. Try again later")
                        return redirect('users:edit_course_details',result[1].pk)
            context = {
                'page_title':'Check Mate',
                'user_type':type_of_logged_in_user,
                'media_url':settings.MEDIA_URL,
                'logged_in_user':logged_in_user,
                'year':datetime.now().year,
                'course':course,

            }
            return render(request,"course_edit.html",context)
        else:
            return HttpResponse("Not Allowed")


    except Exception as e:
        #saving error information in database if error occured
        logger.error("An error occurred for during logging in at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.save_system_errors(user,error_name=e,error_traceback=traceback.format_exc())
        return HttpResponse("Bad Request")