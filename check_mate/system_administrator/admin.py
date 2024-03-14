from django.contrib import admin
from .models import *

#Registering the models created here otherwise the tables won't show up on
#the admin panel

# Register your models here.
@admin.register(System_Errors)
class System_Errors_Admin_Panel(admin.ModelAdmin):
    list_display = [
        'date_time','error_name','error_occured_for','error_traceback','error_fix_status'
    ]