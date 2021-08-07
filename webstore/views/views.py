from django.shortcuts import redirect, render
from webstore.models import User

# Create your views here.

def home(request):
    return render(request, "webstore/home.html")

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            exists = (User.objects.filter(userName = username).exists() and User.objects.filter(password = password).exists())
            if exists:
                return render(request, "webstore/home.html")
        return render(request, "webstore/login.html")
    else:
        return render(request, "webstore/login.html")