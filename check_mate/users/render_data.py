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
            all_courses = Course_Section.objects.filter(semester = semester,year = semester.year)
        elif 2 in roles:
            try:
                #getting students courses
                student_courses = Student.objects.get(student_id = logged_in_user,semester = semester,year = semester.year)

                for course in student_courses.courses.all():
                    
                    course_obj = Course.objects.get(id = course.pk)
                    specific_course = Course_Section.objects.filter(course_id = course_obj,semester = semester,year = semester.year)
                    #checking which course section belongs to this student
                    for i in specific_course:
                        try:
                            stud = None
                            stud = i.students.get(student_id = logged_in_user)
                            if stud:
                                all_courses.append(i)
                                break
                        except:
                            pass
                    print(all_courses)
                try:
                    #if the student is also a TA then loading those courses as well
                    ta_courses = Teaching_Assistant.objects.get(student_id = logged_in_user,semester = semester,year = semester.year)
                    for course in ta_courses.courses.all():
                        specific_course = Course_Section.objects.filter(course_id = course,semester = semester,year = semester.year)
                        for i in specific_course:
                            try:
                                ta = None
                                ta = i.teaching_assistant.get(teaching_id = logged_in_user)
                                if ta and i not in all_courses:
                                    all_courses.append(i)
                                    break
                            except:
                                pass
                except:
                    pass
            except:
                pass

        elif 1 in roles:
            try:
                #loading instructors courses
                instructor_courses = Instructor.objects.get(instructor_id = logged_in_user,semester = semester,year = semester.year)
                for course in instructor_courses.courses.all():
                    specific_course = Course_Section.objects.filter(course_id = course,semester = semester,year = semester.year)
                    for i in specific_course:
                        all_courses.append(i)
            except:
                pass

        return all_courses

    def get_all_courses():

        '''This function will return all the courses that are registered in Course'''

        return Course.objects.all()
    
    def get_specific_course(course_id):

        return Course.objects.get(id = course_id )
    
    def get_specific_course_section(course_id):

        return Course_Section.objects.get(id = course_id)
    
    def get_all_instructors(selected_instructor):


        roles = Roles.objects.get(role_id = 1)
        return School_Users.objects.filter(user_role = roles)

    def get_all_student(selected_students):

        roles = Roles.objects.get(role_id = 2)
        return School_Users.objects.filter(user_role = roles)
        
    def get_selected_ta_students_instructors(course_id):

        '''This function will return the selected instructors, ta and students for a section
            where instructor is just and object but rest two is a list'''
        
        selected_instructor = None
        selected_ta = []
        selected_students = []

        course_section = Course_Section.objects.get(id = course_id)
        teaching_assistant = course_section.teaching_assistant.all()
        instructor = course_section.instructor
        students = course_section.students.all()
        exist = False

        try:
            selected_instructor = instructor.instructor_id
            for i in teaching_assistant:
                selected_ta.append(i.teaching_id)
            for stud in students:
                selected_students.append(stud.student_id)
            exist = True
        except:
            pass

        return (selected_instructor, selected_ta, selected_students,exist)
    
    def get_section_exams(course_id):

        '''This function will return all the exams of a section'''

        course_section = Course_Section.objects.get(pk = course_id)
        sec_exam = Section_Exam.objects.filter(section = course_section)

        return sec_exam
    
    def get_saved_section_exams(exam_id):

        '''This function will return the saved section exams'''

        return Section_Exam.objects.get(pk = exam_id)
    
    def get_set_questions_for_none(exam_id):

        '''This function will load question set of none type'''

        dic={}
        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        if section_exam.exam_set == 0:
            questions = Question.objects.filter(questions_of = section_exam,question_set='A').order_by('-pk')
            dic['A'] = questions

        return dic
    
    def get_set_questions_not_none(exam_id):

        '''This function will load questions sets of not none type'''

        sets = []
        dic={}
        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        for i in range(section_exam.exam_set):
            ascii_value = ord('A') + i
            letter = chr(ascii_value)
            questions = Question.objects.filter(questions_of = section_exam,question_set=letter).order_by('-pk')
            dic={}
            dic[letter]=questions
            sets.append((letter,dic))

        return sets
    
    def get_questions_and_marks_list(exam_id,question_set):

        '''This function will return the a list containing two lists of questions and marks'''

        question_list = []
        marks_list = []
        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        questions = Question.objects.filter(questions_of = section_exam,question_set=question_set).order_by('-pk')
        for q in questions:
            question_list.append(str(q.question))
            marks_list.append(str(q.marks))

        return (question_list,marks_list)
    
class Save:

    '''This class will hold all the functions for saving new data and updating existing one'''

    def save_course(course_code,course_name,course_description,course_picture,course_existing):

        '''This function returns True if successfully saved/updated details of course'''

        if course_existing == None:
            course = Course.objects.create(
                course_code = course_code,course_name = course_name, course_picture = course_picture,
                course_description = course_description
            )
            course.save()

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

    def save_section(section_number,course_id):

        '''This function will add new section to the course'''
        session = Session.objects.get(current = True)
        course = Course.objects.get(pk = course_id)
        try:
            course_sec = Course_Section.objects.get(course_id = course,section_number = section_number,semester = session,year = session.year)
            if course_sec:
                #preventing creating new one as already exists
                return (False,"Section already exists!")
        except:
            pass
        
        course_sec = Course_Section.objects.create(course_id = course,section_number = section_number,semester = session,year = session.year)
        course_sec.save()
        return (True,"Section Created Successfully!")

    def save_course_section_details(section,instructor,ta,students,course_id,flag):

        '''This function will save the students, TA and Instructor for a section'''
        
        session = Session.objects.get(current = True)

        course_section = Load_Courses.get_specific_course_section(course_id)
        instructor = School_Users.objects.get(user_id = instructor)
        ta = School_Users.objects.get(user_id = ta)

        courses = course_section.course_id
        if flag:
            
            old_ta = Teaching_Assistant.objects.get(semester = session,year = session.year,section=section,courses = courses)
            old_ta.delete()
            old_instructor = Instructor.objects.get(semester = session,year = session.year,section=section,courses = courses)
            old_instructor.delete()
            old_students = Student.objects.filter(semester = session,year = session.year,section=section,courses = courses)
            for i in old_students:
                i.delete()

        ta = Teaching_Assistant.objects.create(teaching_id = ta,semester = session,year = session.year)
        ta.courses.add(courses)
        ta.semester = session
        ta.year = session.year
        ta.section = section
        ta.save()

        instructor = Instructor.objects.create(instructor_id = instructor,semester = session,year = session.year)
        instructor.courses.add(courses)
        instructor.semester = session
        instructor.year = session.year
        instructor.section = section
        instructor.save()

        student_list = []
        for i in students:
            inst = School_Users.objects.get(user_id = i)
            stud = Student.objects.create(student_id = inst,semester = session,year = session.year)
            stud.courses.add(courses)
            stud.semester = session
            stud.year = session.year
            stud.section = section
            stud.save()
            student_list.append(stud)

        course_section.section_number = section
        course_section.instructor = instructor
        course_section.teaching_assistant.add(ta)
        course_section.students.add(*student_list)
        course_section.semester = session
        course_section.year = session.year

        course_section.save()

        return (True,"Successfully Saved!")


    def save_exams_for_section(course_id,exam_title,exam_type,exam_mode,exam_date,exam_description,exam_set,exam_id,ta_available):

        '''This function will save/update the exam for a section'''

        course_section = Course_Section.objects.get(pk = course_id)
        exm_type = Exam_Type.objects.get(type_id = exam_type)
        exm_mode = Exam_Mode.objects.get(mode_id = exam_mode)

        try:

            new_instance = Section_Exam.objects.get(pk = exam_id)
            #Updating an existing instance
            new_instance.exam_title = exam_title
            new_instance.exam_type = exm_type
            new_instance.exam_mode = exm_mode
            new_instance.exam_date = exam_date
            new_instance.exam_description = exam_description
            new_instance.exam_set = exam_set
            new_instance.ta_available = ta_available
            new_instance.save()
            message = "Exam Details Updated!"
        except:
            new_instance = Section_Exam.objects.create(section = course_section,
                                                    exam_title = exam_title,
                                                    exam_description = exam_description,
                                                    exam_type = exm_type,
                                                    exam_mode = exm_mode,
                                                    exam_date = exam_date,
                                                    exam_set = exam_set,
                                                    ta_available = ta_available)
            new_instance.save()
            message = "Exam Created Successfully!"
        
        return (True,message,new_instance)

    def save_question_for_exam(exam_id,question_set,question,answer_size,marks,question_id):

        '''This function will save the questions for a particular exam'''

        section_exm = Section_Exam.objects.get(pk = exam_id)
        try:
            quest = Question.objects.get(id = question_id)
            quest.question = question
            quest.answer_field_length = answer_size
            quest.marks = marks
            quest.question_set = question_set
            quest.save()
            message = "Question Updated!"
        except:
            
            question_exam = Question.objects.create(questions_of = section_exm,
                                                    question = question,
                                                    answer_field_length = answer_size,
                                                    marks = marks,
                                                    question_set = question_set)
            question_exam.save()
            message = "Question Saved!"
        return (True,message)


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
            
    def delete_question(pk):

        '''Thus function will delete the question for the specific set'''

        question = Question.objects.get(pk=pk)
        question.delete()

        return True

    def delete_section_exam(exam_id):

        '''This function will delete the exam of a section'''

        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        section_exam.delete()

        return True
