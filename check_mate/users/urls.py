from django.urls import path,include
from . import views

app_name = "users"

urlpatterns = [

    path('',views.check_mate,name="check_mate"),
    path('login/',views.login,name="login"),  
    path('logout/',views.logout,name="logout"),
    path('registration/',views.registration,name = "registration"),   
    path('registration/email_verification/<str:user_id>',views.registration_email_verification,name = "registration_email_verification"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('edit_profile/',views.edit_profile,name="edit_profile"),
    path('courses/',views.courses,name="courses"),
    path('all_courses/',views.all_courses,name="all_courses"),
    path('all_courses/course_edit/<int:course_id>',views.course_edit,name="course_edit"),
]
