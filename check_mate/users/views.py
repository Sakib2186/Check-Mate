from django.shortcuts import render

# Create your views here.
def login(request):

    context = {
        'page_title':"Check Mate"
    }
    return render(request,"login_page.html",context)