from .models import *
from django.contrib.auth.models import User
from check_mate import settings
from django.core.mail import EmailMultiAlternatives
import pyotp
from datetime import datetime,timedelta
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
import random
import fitz
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from io import BytesIO
from ultralytics import YOLO
from PIL import Image
import threading
from ultralytics.engine.results import Results
from ultralytics.utils.plotting import save_one_box
import logging
from io import BytesIO
from django.core.files import File
from pathlib import Path

LOGGER = logging.getLogger(__name__)

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
            print(email_from)
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
            print("email sen22")
            sent_email.send()
            print("email sent")
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

    def get_bar_chart_stats(logged_in_user):

        semester = Session.objects.get(current=True)
        #role of user
        roles = []
        if logged_in_user == None:
            roles.append(3)
        else:
            user_role = logged_in_user.user_role.all()
            for i in user_role:
                roles.append(i.role_id)
        courses_list = []
        count_list = []
        all_courses = []
        highest_achiever = []
        highest_marks = []
        #getting all courses of this user
        if 3 in roles:
            #as admin so getting all courses
            all_courses = Course_Section.objects.filter(semester = semester,year = semester.year)
            for course in all_courses:
                sec_exam_count = Section_Exam.objects.filter(section = course).count()
                name_sec = f"{course.course_id.course_code}.{course.section_number}"
                courses_list.append(name_sec)
                count_list.append(sec_exam_count)

                sec_exam = Section_Exam.objects.filter(section = course,exam_type = Exam_Type.objects.get(type_id = 1)).order_by('-pk')[:1]
                print(sec_exam)
                highest_mark = Students_Score.objects.filter(exam_of = sec_exam).order_by('-score').first()
                
                if highest_mark == None:
                    continue
                print(highest_mark.student.user_id)
                new = f"{highest_mark.exam_of.section.course_id.course_code}.{highest_mark.exam_of.section.section_number}"
                highest_achiever.append(new)
                highest_marks.append(highest_mark.score)
        elif 2 in roles:
            try:
                #getting students courses
                student_courses = Student.objects.filter(student_id = logged_in_user,semester = semester,year = semester.year)

                for course in student_courses:

                    course_obj = Course.objects.get(id = course.courses.pk)
                    specific_course = Course_Section.objects.filter(course_id = course_obj,semester = semester,year = semester.year,section_number = course.section)

                    #checking which course section belongs to this student
                    for i in specific_course:
                        try:
                            stud = None
                            stud = i.students.get(student_id = logged_in_user)
                            if stud:
                                all_courses.append(i)
                                
                        except:
                            pass
                    for course in all_courses:
                        sec_exam_count = Section_Exam.objects.filter(section = course).count()
                        name_sec = f"{course.course_id.course_code}.{course.section_number}"
                        courses_list.append(name_sec)
                        count_list.append(sec_exam_count)

                        sec_exam = Section_Exam.objects.filter(section = course,exam_type = Exam_Type.objects.get(type_id = 1)).order_by('-pk')[:1]
                        print(sec_exam)
                        highest_mark = Students_Score.objects.filter(exam_of = sec_exam).order_by('-score').first()
                        
                        if highest_mark == None:
                            continue
                        print(highest_mark.student.user_id)
                        new = f"{highest_mark.exam_of.section.course_id.course_code}.{highest_mark.exam_of.section.section_number}"
                        highest_achiever.append(new)
                        highest_marks.append(highest_mark.score)
            except:
                pass

        elif 1 in roles:
            try:
                #loading instructors courses
                instructor_courses = Instructor.objects.filter(instructor_id = logged_in_user,semester = semester,year = semester.year)
                for course in instructor_courses:
                    specific_course = Course_Section.objects.filter(course_id = course.courses.pk,semester = semester,year = semester.year,section_number = course.section)
                    for i in specific_course:
                        all_courses.append(i)
            except:
                pass
            for course in all_courses:
                sec_exam_count = Section_Exam.objects.filter(section = course).count()
                name_sec = f"{course.course_id.course_code}.{course.section_number}"
                courses_list.append(name_sec)
                count_list.append(sec_exam_count)

                sec_exam = Section_Exam.objects.filter(section = course,exam_type = Exam_Type.objects.get(type_id = 1)).order_by('-pk')[:1]
                print(sec_exam)
                highest_mark = Students_Score.objects.filter(exam_of = sec_exam).order_by('-score').first()
                
                if highest_mark == None:
                    continue
                print(highest_mark.student.user_id)
                new = f"{highest_mark.exam_of.section.course_id.course_code}.{highest_mark.exam_of.section.section_number}"
                highest_achiever.append(new)
                highest_marks.append(highest_mark.score)

        return (courses_list[:6],count_list[:6],highest_achiever[:6],highest_marks[:6])


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
                student_courses = Student.objects.filter(student_id = logged_in_user,semester = semester,year = semester.year)

                for course in student_courses:

                    course_obj = Course.objects.get(id = course.courses.pk)
                    specific_course = Course_Section.objects.filter(course_id = course_obj,semester = semester,year = semester.year,section_number = course.section)

                    #checking which course section belongs to this student
                    for i in specific_course:
                        try:
                            stud = None
                            stud = i.students.get(student_id = logged_in_user)
                            if stud:
                                all_courses.append(i)
                                
                        except:
                            pass
   
                try:
                    #if the student is also a TA then loading those courses as well
                    ta_courses = Teaching_Assistant.objects.filter(teaching_id = logged_in_user,semester = semester,year = semester.year)
                    for course in ta_courses:
                        specific_course = Course_Section.objects.filter(course_id = course.courses.pk,semester = semester,year = semester.year,section_number = course.section)
                        for i in specific_course:
                            try:
                                ta = None
                                ta = i.teaching_assistant.get(teaching_id = logged_in_user)
                                if ta:
                                    if i not in all_courses:
                                        all_courses.append(i)
                            except:
                                pass
                except:
                    pass
            except:
                pass

        elif 1 in roles:
            try:
                #loading instructors courses
                instructor_courses = Instructor.objects.filter(instructor_id = logged_in_user,semester = semester,year = semester.year)
                for course in instructor_courses:
                    specific_course = Course_Section.objects.filter(course_id = course.courses.pk,semester = semester,year = semester.year,section_number = course.section)
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

        '''This function will return all the exams of a section along with the number of students
            in each section'''

        course_section = Course_Section.objects.get(pk = course_id)
        sec_exam = Section_Exam.objects.filter(section = course_section)
        dic={}
        for sec in sec_exam:
            total_student_enrollment = sec.section.students.all().count()
            dic[sec] = total_student_enrollment

        return dic
    
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
        answer_length = []
        question_images = []
        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        questions = Question.objects.filter(questions_of = section_exam,question_set=question_set).order_by('-pk')
        for q in questions:
            question_list.append(str(q.question))
            marks_list.append(str(q.marks))
            answer_length.append(q.answer_field_length_number)
            if q.question_image:
                question_images.append(q.question_image)
            else:
                question_images.append(None)

        return (question_list,marks_list,answer_length,question_images)
    
    def get_question_and_marks(exam_id,set_number):

        '''This function will return a questions of that set'''

        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        total_marks = 0
        if set_number == "all":
            question =  Question.objects.filter(questions_of = section_exam).order_by('-pk')
            for mark in question:
                total_marks += mark.marks
        else:
            question =  Question.objects.filter(questions_of = section_exam,question_set=set_number).order_by('-pk')
            for mark in question:
                total_marks += mark.marks

        return (question,total_marks)
    
    def load_set_of_student(user,course_id):
        
        '''This function will return the students set for the exam
        if admin or instructor then can view all'''
        
        course_section = Course_Section.objects.get(pk = course_id)
        try:
            student = Student.objects.get(student_id = user)
            set_student = Shuffled_Papers.objects.get(student = student,course_id = course_section)
            return set_student.set_name
        except:
            return "all"
    
    def load_updated_time(exam_id):

        '''This function will return the updated time each time the page is loaded'''

        section_exam = Load_Courses.get_saved_section_exams(exam_id)

        current_date = datetime.now()
        time = section_exam.exam_time
        time = time.split(' ')
        number = time[0]
        minute_or_hour = time[1]

    def get_exam_uploaded_students(exam_id):

        '''This function will return the students who have uploaded their work'''

        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        submitted_exam = Exam_Submitted.objects.filter(exam_of = section_exam,is_uploaded = True)

        return submitted_exam
    
    def get_all_students_submission(exam_id):

        '''This function will return all the submission details of student'''

        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        papers = Exam_Submitted.objects.filter(exam_of = section_exam)

        return papers

    def get_question_and_answer_of_student(exam_id,student_id):

        '''This function will return the questions and answer of that question of a student'''
        
        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        student = School_Users.objects.get(user_id = student_id)
        ins = Student.objects.get(student_id =student,courses = section_exam.section.course_id,section = section_exam.section.section_number)
        student_set = Shuffled_Papers.objects.get(student = ins, course_id = section_exam.section)
        questions = Question.objects.filter(questions_of = section_exam,question_set = student_set.set_name).order_by('-pk')
        question_answer = {}
        set_number = ""
        first_question = Question.objects.filter(questions_of = section_exam,question_set = student_set.set_name).first()

        total_marks = 0
        score = 0
        for question in questions:

            answer = Answer.objects.get(answer_of = question,uploaded_by = student)
            question_answer[question] = answer
            set_number = question.question_set
            total_marks += question.marks
            score += answer.marks_obtained 
            #here giving algo to store marks of students
        
        student_score = Students_Score.objects.get(exam_of = section_exam,student = student)
        student_score.total_marks = total_marks
        student_score.score = score
        student_score.save()


        return (question_answer,student,total_marks,score,set_number,first_question)
    
    def number_of_quizzes_and_midterm(course_id):

        '''This function returns the number of quizzes held in the section'''

        course_section = Load_Courses.get_specific_course_section(course_id)
        section_exam = Section_Exam.objects.filter(section = course_section)

        quiz_number = []
        midterm_number = []
        final = []

        for exams in section_exam:
            if exams.exam_type.type_id == 1:
                quiz_number.append(exams)
            elif exams.exam_type.type_id == 2:
                midterm_number.append(exams)
            elif exams.exam_type.type_id == 3:
                final.append(exams)

        return (quiz_number,midterm_number,final)
    
    def load_spreadsheet_info(course_id,quizzes_number):

        '''This function will return the average of all quizzes if All is choosen
            else the best quizzes average would be returned'''
        
        course_section = Load_Courses.get_specific_course_section(course_id)
        section_exams = Section_Exam.objects.filter(section=course_section)
        students = course_section.students.all()
        
        student_scores = {}

        # Initialize dictionaries to store scores for each type
        quiz_scores = {student: [] for student in students}
        mid_scores = {student: [] for student in students}
        final_scores = {student: [] for student in students}


        for exam in section_exams:
            for student in students:
                stud = School_Users.objects.get(user_id = student)
                student_score = Students_Score.objects.get(exam_of=exam, student=stud)

                if exam.exam_type.type_id == 1:
                    quiz_scores[student].append(student_score.score)
                elif exam.exam_type.type_id == 2:
                    mid_scores[student].append(student_score.score)
                elif exam.exam_type.type_id == 3:
                    final_scores[student].append(student_score.score)

        # Calculate average scores based on the choice
        for student in students:
            if quizzes_number == 'All':
                quiz_avg = sum(quiz_scores[student]) / len(quiz_scores[student]) if quiz_scores[student] else 0
            else:
                quizzes_number = int(quizzes_number)
                if quizzes_number >= 1:  # Ensure at least one quiz is selected
                    quiz_avg = sum(sorted(quiz_scores[student], reverse=True)[:quizzes_number]) / quizzes_number if quiz_scores[student] else 0
                else:
                    quiz_avg = 0

            mid_avg = sum(mid_scores[student]) / len(mid_scores[student]) if mid_scores[student] else 0
            final_avg = sum(final_scores[student]) / len(final_scores[student]) if final_scores[student] else 0

            stud = School_Users.objects.get(user_id = student)
            result = quiz_avg * (15/100) + mid_avg * (35/100) + final_avg * (40/100) 
            student_scores[stud] = {
            'Quizzes': quiz_scores[student],
            'Quiz Average': quiz_avg,
            'Mids': mid_scores[student],
            'Midterm Average': mid_avg,
            'Final Average': final_avg,
            'result':result,
            }

        return student_scores
    
    def load_announcements(logged_in_user,type_of_logged_in_user):

        '''This function will load all the announcements'''

        if logged_in_user == None:
            return Announcements.objects.all().order_by('-pk')
        session = Session.objects.get(current = True)

        ann = []
        if 1 in type_of_logged_in_user:
            intstructor = Instructor.objects.filter(instructor_id=logged_in_user,semester = session,year = session.year)
            
            for course in intstructor:
                course_section = Course_Section.objects.get(course_id = course.courses)
                section_exam = Section_Exam.objects.filter(section = course_section)
                for exam in section_exam:
                    ann = ann + list(Announcements.objects.filter(section_exam = exam).order_by('-pk'))
            return ann
        if 2 in type_of_logged_in_user:
            students = Student.objects.filter(student_id=logged_in_user,semester = session,year = session.year)
            for course in students:
                course_section = Course_Section.objects.get(course_id = course.courses)
                section_exam = Section_Exam.objects.filter(section = course_section)
                for exam in section_exam:
                    ann =ann + list(Announcements.objects.filter(section_exam = exam.pk).order_by('-pk'))
            return ann
                

    def load_students_answer(exam_id,student_id):

        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        question_answer_list = {}
        session = Session.objects.get(current = True)
        if section_exam.exam_mode.mode_id == 1 and student_id != None and student_id != 0:

            shuffeled = Shuffled_Papers.objects.get(student = Student.objects.get(courses=section_exam.section.course_id,semester=session,student_id =  School_Users.objects.get(user_id = student_id)),course_id = section_exam.section)
            questions = Question.objects.filter(questions_of = section_exam,question_set = shuffeled.set_name).order_by('pk')
            
            for q in questions:
                answer = Answer.objects.get(answer_of = q,uploaded_by = School_Users.objects.get(user_id = student_id))
                question_answer_list[q] = answer

        return question_answer_list








        

    
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
        ta.courses = courses
        ta.semester = session
        ta.year = session.year
        ta.section = section
        ta.save()

        instructor = Instructor.objects.create(instructor_id = instructor,semester = session,year = session.year)
        instructor.courses = courses
        instructor.semester = session
        instructor.year = session.year
        instructor.section = section
        instructor.save()

        student_list = []
        for i in students:
            inst = School_Users.objects.get(user_id = i)
            stud = Student.objects.create(student_id = inst,semester = session,year = session.year)
            stud.courses = courses
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

            print(new_instance.exam_set)
            print(int(exam_set))
            if new_instance.exam_set != int(exam_set):

                print("here")
 
                questions = Question.objects.filter(questions_of = new_instance)
 
                for question in questions:
                    path = settings.MEDIA_ROOT+str(question.question_image)

                    if os.path.isfile(path):

                        os.remove(path)

                    question.delete()

            new_instance.exam_set = exam_set

            new_instance.ta_available = ta_available

            new_instance.save()
            all_students = new_instance.section.students.all()

            for student in all_students:
                try:
                    old = Exam_Submitted.objects.get(exam_of = new_instance,student = student.student_id)
                    old_score = Students_Score.objects.get(exam_of = new_instance,student = student.student_id,exam_type = exm_type)
                    if old:
                        pass
                    if old_score:
                        pass
                except:
                    exm_submit = Exam_Submitted.objects.create(exam_of = new_instance,student = student.student_id)
                    exm_submit.save()
                    exm_score = Students_Score.objects.create(exam_of = new_instance,student = student.student_id,exam_type = exm_type)
                    exm_score.save()
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
            all_students = new_instance.section.students.all()
            for student in all_students:
                exm_submit = Exam_Submitted.objects.create(exam_of = new_instance,student = student.student_id)
                exm_submit.save()
                exm_score = Students_Score.objects.create(exam_of = new_instance,student = student.student_id,exam_type = exm_type)
                exm_score.save()
            message = "Exam Created Successfully!"
        
        return (True,message,new_instance)

    def save_question_for_exam(exam_id,question_set,question,answer_size,marks,box_height,question_image,question_id):

        '''This function will save the questions for a particular exam'''

        section_exm = Section_Exam.objects.get(pk = exam_id)
        try:
            quest = Question.objects.get(id = question_id)
            quest.question = question
            quest.answer_field_length = answer_size
            quest.marks = marks
            quest.question_set = question_set
            quest.answer_field_length_number = box_height
            if question_image != None:
                path = settings.MEDIA_ROOT+str(quest.question_image)
                if os.path.isfile(path):
                    os.remove(path)
            quest.question_image = question_image
            quest.save()
            message = "Question Updated!"
        except:
            question_exam = Question.objects.create(questions_of = section_exm,
                                                    question = question,
                                                    answer_field_length = answer_size,
                                                    marks = marks,
                                                    answer_field_length_number = box_height,
                                                    question_set = question_set,
                                                    question_image = question_image)
            question_exam.save()
            all_students = section_exm.section.students.all()
            for student in all_students:
                answer = Answer.objects.create(answer_of = question_exam,uploaded_by =student.student_id)
                answer.save()
                try:
                    shuff = Shuffled_Papers.objects.get(student = student,course_id = section_exm.section)
                except:
                    shuff = Shuffled_Papers.objects.create(student = student,course_id = section_exm.section,set_name = "A")
                shuff.save()
            message = "Question Saved!"
        return (True,message)

    def shuffled_papers(course_id):

        '''This function will shuffle the papers everytime the instructor clicks start'''
        
        course_section = Load_Courses.get_specific_course_section(course_id)

        try:
            shuffled_papers_of_this_section = Shuffled_Papers.objects.filter(course_id = course_section)
            shuffled_papers_of_this_section.delete()
        except:
            pass

        
        all_students = course_section.students.all()

        all_sets = Question.objects.values_list('question_set',flat=True).distinct()
        all_sets = list(all_sets)
        all_sets_length = len(all_sets)


        if all_sets_length==1:
            for student in all_students:
                shuffled_paper = Shuffled_Papers.objects.create(student = student,course_id = course_section,set_name = all_sets[0])
                shuffled_paper.save()
        else:
            student_list = list(all_students)
            random.shuffle(student_list)
            shuffled_students = Student.objects.filter(pk__in=[obj.pk for obj in student_list])
            for student in shuffled_students:
                random_set = random.randint(0, all_sets_length-1)

                shuffled_paper = Shuffled_Papers.objects.create(student = student,course_id = course_section,set_name = all_sets[random_set])
                shuffled_paper.save()

        return True

    def start_exam(exam_id):

        '''This function will start the exam'''

        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        section_exam.is_started=True
        section_exam.save()
        return True
    
    def uploaded_answer_file(user,file,exam_id,student_id = None):

        '''This method will save the file uploaded by the user'''

        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        session = Session.objects.get(current = True)
        if section_exam.exam_mode.mode_id == 3:
            student_id = user.user_id
        shuffeled = Shuffled_Papers.objects.get(student = Student.objects.get(courses=section_exam.section.course_id,semester=session,student_id =  School_Users.objects.get(user_id = student_id)),course_id = section_exam.section)
        questions = Question.objects.filter(questions_of = section_exam,question_set = shuffeled.set_name).order_by('pk')
        
        count = 0
        ####here apply question
        pdf = file
        pdf_bytes = pdf.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        img_dir = os.path.join(settings.MEDIA_ROOT, 'predicted_images')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        saved_image_paths = []
        result = []
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            image_bytes = pix.tobytes() 
            img = Image.open(BytesIO(image_bytes))
            saved_image_paths.append(Save.save_image(img, exam_id, i))
        
        for img_path in saved_image_paths:
            img = Image.open(img_path)
            result += Save.apply_yolo_detection(img)
            # Process YOLO detection results as needed
            # Delete the temporary image file after processing
            os.remove(img_path)
        len(result)
        for r in range(len(result)):
            Results.save_crop = Save.custom_save_crop
            result[r].save_crop(save_dir=img_dir, file_name="crop_image.jpg")

        idx= 0
        for img_file in sorted(os.listdir(img_dir)):

            if img_file.startswith("crop_image") and img_file.endswith(".jpg"):
                print("inside")
                img_path = os.path.join(img_dir, img_file)
                try:
                    img_number = int(img_file[len("crop_image"):-len(".jpg")])
                except:
                    img_number = 1
                # Load the cropped image
                cropped_img = Image.open(img_path)

                # Save the cropped image to a BytesIO object
                img_byte_arr = BytesIO()
                cropped_img.save(img_byte_arr, format='JPEG')
                img_byte_arr.seek(0)
                
                django_file = File(img_byte_arr, name=img_file)
                # # Save the cropped image to the Answer model
                answer = Answer.objects.get(
                    answer_of = questions[idx],
                    uploaded_by=School_Users.objects.get(user_id = student_id))
                path = settings.MEDIA_ROOT+str(answer.answer_image)
                if os.path.isfile(path):
                    os.remove(path)
                answer.answer_image.save(img_file, django_file)
                answer.save()
                idx += 1
                # # Clean up the cropped image file
                os.remove(img_path)

        
        if section_exam.exam_mode.mode_id == 3:
            if user == None:
                return False

            exm_submit = Exam_Submitted.objects.get(exam_of = section_exam,student = user)
            exm_submit.is_uploaded = True
            exm_submit.save()
        elif section_exam.exam_mode.mode_id == 1:
            exm_submit = Exam_Submitted.objects.get(exam_of = section_exam,student = School_Users.objects.get(user_id = student_id))
            exm_submit.is_uploaded = True
            exm_submit.save()


        return True

    def save_image(img, exam_id, page_num):
        # Save the image to a temporary location
        img_dir = os.path.join(settings.MEDIA_ROOT, 'temporary_images')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        img_path = os.path.join(img_dir, f"temp_page_{page_num}_exam_{exam_id}.jpg")
        img.save(img_path)
        return img_path

    def apply_yolo_detection(img):
        # Apply YOLO object detection on the image
        model = YOLO('yolov8predict.pt') 
        result = model.predict(img,imgsz=320, conf=0.5)
        return result

    def save_marks_comment(question_pk,marks,comment,student_id):

        '''Thus function will save the marks and comments for a answer'''

        question = Question.objects.get(pk = question_pk)
        answer = Answer.objects.get(answer_of = question,uploaded_by = School_Users.objects.get(user_id = student_id))

        answer.marks_obtained = marks
        answer.comment = comment        
        
        answer.save()

        return True
    
    def save_announcement(logged_in_user,section_exam,announcement):

        '''This function will save the announcement'''

        try:
            annouce = Announcements.objects.get(section_exam = section_exam)
        except:
            annouce = Announcements.objects.create(section_exam = section_exam)
        annouce.announcement = announcement
        if logged_in_user == None:
            annouce.given_by = "Admin"
        else:
            annouce.given_by = logged_in_user
        annouce.save()

        return True
    
    def custom_save_crop(self, save_dir, file_name=Path("im.jpg")):
        """
        Save cropped predictions to `save_dir/file_name.jpg`.

        Args:
            save_dir (str | pathlib.Path): Save path.
            file_name (str | pathlib.Path): File name.
        """
        if self.probs is not None:
            LOGGER.warning("WARNING ⚠️ Classify task do not support `save_crop`.")
            return
        if self.obb is not None:
            LOGGER.warning("WARNING ⚠️ OBB task do not support `save_crop`.")
            return
        for d in self.boxes:
            save_one_box(
                d.xyxy,
                self.orig_img.copy(),
                file=Path(save_dir) / f"{Path(file_name).stem}.jpg",
                BGR=True,
            )

    def update_profile_picture(profile_picture,user):

        path = settings.MEDIA_ROOT+str(user.user_profile_picture)
        if os.path.isfile(path):
            os.remove(path)
        user.user_profile_picture = profile_picture
        user.save()

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
            
    def delete_question(pk):

        '''Thus function will delete the question for the specific set'''

        question = Question.objects.get(pk=pk)
        answer = Answer.objects.filter(answer_of = question)
        for ans in answer:
            path = settings.MEDIA_ROOT+str(ans.answer_image)
            if os.path.isfile(path):
                os.remove(path)
            ans.delete()
        question.delete()

        return True

    def delete_section_exam(exam_id):

        '''This function will delete the exam of a section'''

        section_exam = Load_Courses.get_saved_section_exams(exam_id)
        questions = Question.objects.filter(questions_of = section_exam)
        for question in questions:
            path = settings.MEDIA_ROOT+str(question.question_image)
            if os.path.isfile(path):
                os.remove(path)
            question.delete()
        section_exam.delete()

        return True