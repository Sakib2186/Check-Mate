from django.contrib import admin
from .models import *


#Registering the models created here otherwise the tables won't show up on
#the admin panel

# Register your models here.
@admin.register(Roles)
class Roles_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'role_id','role_name'
    ]
@admin.register(School_Users)
class School_Users_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'pk','user_id','user_first_name','user_middle_name','user_last_name','user_email',
        'user_phone_number','user_profile_picture','user_otp_verified'
    ]
@admin.register(Course)
class Course_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'course_code','course_name','course_picture',
        'course_description'
    ]
@admin.register(Student)
class Student_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'student_id','courses','semester','year','section'
    ]
@admin.register(Instructor)
class Instructor_Admin_Panel(admin.ModelAdmin):
    list_display=[
        'instructor_id','courses','semester','year','section'
    ]
@admin.register(Teaching_Assistant)
class Teaching_Asistant_Admin_Panel(admin.ModelAdmin):
    list_display=[
        'teaching_id','courses','semester','year','section'
    ]
@admin.register(Course_Section)
class Course_Section_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'pk','course_id','section_number','instructor','semester','year'
    ]
@admin.register(Session)
class Session_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'session_name','session_id','current','year'
    ]
@admin.register(Exam_Type)
class Exam_Type_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'type_id','exam_type'
    ]
@admin.register(Exam_Mode)
class Exam_Mode_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'mode_id','mode'
    ]
@admin.register(Section_Exam)
class Section_Exam_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'pk','section','exam_title','exam_description','exam_type','exam_mode','exam_date','exam_time','exam_set','ta_available',
        'is_started','is_stopped','is_completed','is_checked'
    ]
@admin.register(Question)
class Question_Admin_panel(admin.ModelAdmin):
    list_display = [
        'pk','questions_of','question_number','question','answer_field_length','answer_field_length_number','marks','question_set','question_image'
    ]
@admin.register(Answer)
class Answer_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'pk','answer_of','uploaded_by','answer_textfield','answer_image','marks_obtained','comment'
    ]
@admin.register(Shuffled_Papers)
class Suffple_Papers_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'student','course_id','set_name'
    ]
@admin.register(Exam_Submitted)
class Exam_Submitted_Admin_Panel(admin.ModelAdmin):
    list_display=[
        'exam_of','student','is_uploaded'
    ]