from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, "webstore/home.html")

def login(request):
    return render(request, "webstore/login.html")