from .models import *
from django.contrib.auth.models import User
from check_mate import settings
from django.core.mail import send_mail,EmailMultiAlternatives
import pyotp
from datetime import datetime,timedelta
from django.template.loader import render_to_string
from django.utils.html import strip_tags
class Login:

    '''This class will hold all the functionalities to log in and regsitration of new user'''

    def register_user(request,user_name,password,confirm_password):

        '''Registers a user to the database if he is not registered yet'''
        
        #declaring a message variable to return different message according to condition
        message = ""

        if password == confirm_password:
            #checking to see if password is more than 6 characters
            if len(password)>6:

                try:
                    #getting registered school user from our database
                    get_school_user = School_Users.objects.get(user_id = user_name)
                    #checking if user is already signed up
                    if User.objects.filter(username = user_name).exists():
                        message = "You are already signed up! Try Logging in instead."
                        #returning message as tuple
                        return (False,message)
                    else:
                        #user not signed up so creating new User by first sending otp to their email
                        if Login.registration_email(request,get_school_user):
                            user = User.objects.create_user(username = get_school_user.user_id,email=get_school_user.user_email,password=password)
                            user.save()
                            return (True,get_school_user)
                        else:
                            message = "Something went wrong! Try again"
                            #returning message as tuple
                            return (False,message) 
                        
                except School_Users.DoesNotExist:
                    message = "Looks like you are not a registered User.\n"+ \
                               "Contact your IT for assistance."
                    #returning message as tuple
                    return  (False,message)  
            else:
                message = "Password must be greater than 6 characters"
                #returning message as tuple
                return  (False,message)
        else:
            message = "Passwords did not match. Try again"
            #returning message as tuple
            return (False,message)
        
    def registration_email(request,user):

        '''This function will send the email to with the otp to the user'''
        #creating otp
        totp = pyotp.TOTP(pyotp.random_base32(),interval=60)
        otp = totp.now()
        request.session['otp_secret_key']=totp.secret
        valid_date = datetime.now() + timedelta(minutes=1)
        request.session['otp_valid_date'] = str(valid_date)
        print(otp)
        #sending email to user
        try:
            context = {
                'user':user,
                'otp':otp,
                'year':datetime.now().year,

            }
            html_message = render_to_string("email_otp.html",context)
            plain_message = strip_tags(html_message)

            email_from = settings.EMAIL_HOST_USER
            subject="Registration OTP"
            recipient_list = []
            recipient_list.append(user.user_email)

            sent_email = EmailMultiAlternatives(
                subject= subject,
                body = plain_message,
                from_email=email_from,
                to = recipient_list,
            )
            sent_email.attach_alternative(html_message,"text/html")
            sent_email.send()
            return True
        
        except:
            #email could not be sent
            return False