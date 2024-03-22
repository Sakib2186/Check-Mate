from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
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
]
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)