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

@admin.register(School_User_Token)
class School_User_Token_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'user','token'
    ]