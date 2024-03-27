from .models import *
from django.contrib.auth.models import User
from check_mate import settings
from django.core.mail import EmailMultiAlternatives
import pyotp
from datetime import datetime,timedelta
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
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
        
    def logged_in_user(request):

        '''This function will return the user that logged in'''

        logged_in_user = request.user.username
        try:
            user = School_Users.objects.get(user_id = logged_in_user)
        except:
            #admin user
            user=None
        
        return user
        
    def user_type_logged_in(request):

        '''This function will return which user logged in whether it is a
            Instructor or Student'''
        
        logged_in_user = request.user.username

        type = []
        try:
            #trying to get school using
            user = School_Users.objects.get(user_id = logged_in_user)
            #getting the list of all roles for this user
            role_type = user.user_role.all()
            for role in role_type:
                if role.role_id== int(1):
                    type.append(role.role_id)
                if role.role_id == int(2):
                    type.append(role.role_id)
        except:
            #else it is admin
            #3 is not saved in database but we are referring 3 as super user (Admin)
            type.append(3)

        return type

class Load_Courses:

    def get_user_courses(logged_in_user):

        #semester
        semester = Session.objects.get(current=True)
        #role of user
        roles = []
        if logged_in_user == None:
            roles.append(3)
        else:
            user_role = logged_in_user.user_role.all()
            for i in user_role:
                roles.append(i.role_id)
        
        all_courses = []
        #getting all courses of this user
        if 3 in roles:
            #as admin so getting all courses
            all_courses = Course_Section.objects.filter(semester_id = semester.session_id)
        elif 2 in roles:
            #getting students courses
            student_courses = Student.objects.get(student_id = logged_in_user,semester_id = semester.session_id)
            for course in student_courses.courses.all():
                specific_course = Course_Section.objects.get(course_id = course)
                all_courses.append(specific_course)
            try:
                #if the student is also a TA then loading those courses as well
                ta_courses = Teaching_Assistant.objects.get(student_id = logged_in_user,semester_id = semester.session_id)
                for course in ta_courses.courses.all():
                    specific_course - Course_Section.objects.get(course_id = course)
                    if specific_course not in all_courses:
                        all_courses.append(specific_course)
            except:
                pass

        elif 1 in roles:
            #loading instructors courses
            instructor_courses = Instructor.objects.get(instructor_id = logged_in_user,semester_id = semester.session_id)
            for course in instructor_courses.courses.all():
                specific_course = Course_Section.objects.get(course_id = course)
                all_courses.append(specific_course)

        return all_courses

    def get_all_courses():

        '''This function will return all the courses that are registered in Course'''

        return Course.objects.all()
    
    def get_specific_course(course_id):

        return Course.objects.get(id = course_id )
            
class Save:

    '''This class will hold all the functions for saving new data and updating existing one'''

    def save_course(course_code,course_name,course_description,course_picture,course_existing):

        '''This function returns True if successfully saved/updated details of course'''
        #current semeter
        semester = Session.objects.get(current=True)

        if course_existing == None:
            course = Course.objects.create(
                course_code = course_code,course_name = course_name, course_picture = course_picture,
                course_description = course_description
            )
            course.save()
            #linking with Course Section
            course_section = Course_Section.objects.create(course_id = course,semester = semester)
            course_section.save()

            return (True,course)
        else:
            course_existing.course_code = course_code
            course_existing.course_name = course_name
            course_existing.course_description = course_description
            if course_picture != None:
                path = settings.MEDIA_ROOT+str(course_existing.course_picture)
                if os.path.isfile(path):
                    os.remove(path)
                course_existing.course_picture = course_picture
            course_existing.save()

            return (True,course_existing)
        
    def save_semester(semester,year):

        '''This function will save which semester is current and the rest would be off'''
        try:
            session = Session.objects.get(current = True)
            session.current=False
            session.save()
        except:
            pass
        try:
            result = Session.objects.get(session_id = semester, year = year)
            result.current = True
            result.save()         
        except:
            session_name = ""
            if semester== 1:
                session_name="Spring"
            elif semester == 2:
                session_name = "Summer"
            elif semester == 3:
                session_name = "Fall"
            result = Session.objects.create(session_name=session_name,session_id = semester,year=year,current=True)
            result.save()

        return True




class Delete:

    '''This class will hold all the delete functionalities'''

    def delete_course(course_id):

        '''This function will delete the course'''

        course = Course.objects.get(id = course_id)
        #delete the image if any
        #finding the path on the OS
        path = settings.MEDIA_ROOT+str(course.course_picture)
        #if file path exists then deleting it
        if os.path.isfile(path):
            os.remove(path)
        course.delete()
        return True
            