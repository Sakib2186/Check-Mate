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
        'user_id','user_first_name','user_middle_name','user_last_name','user_email',
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
        'student_id','semester','year'
    ]
@admin.register(Instructor)
class Instructor_Admin_Panel(admin.ModelAdmin):
    list_display=[
        'instructor_id','semester','year'
    ]
@admin.register(Teaching_Assistant)
class Teaching_Asistant_Admin_Panel(admin.ModelAdmin):
    list_display=[
        'teaching_id','semester','year'
    ]
@admin.register(Course_Section)
class Course_Section_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'course_id','section_number','instructor','semester','year'
    ]
@admin.register(Session)
class Session_ADmin_Panel(admin.ModelAdmin):
    list_display = [
        'session_name','session_id','current','year'
    ]
