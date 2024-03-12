from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = "users"

urlpatterns = [

    path('login/',views.login,name="login"),      
 
]
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)