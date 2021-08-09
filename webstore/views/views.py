from django.shortcuts import redirect, render
from webstore.models import User

# Create your views here.
loggedUser = None
class LoggedUser:
    logged = False
    def __init__(self, userID, userName, password, name, surname):
        self.userID = userID
        self.userName = userName
        self.password = password
        self.name = name
        self.surname = surname
        self.logged = True

def home(request):
    if(loggedUser is not None and loggedUser.logged):
        return render(request, "webstore/homeLogged.html")
    return render(request, "webstore/home.html")

def login(request):
    global loggedUser
    if loggedUser is not None:
        return redirect("home")
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            user = (User.objects.filter(userName = username, password = password))
            if user:
                loggedUser = LoggedUser(user[0].userID, user[0].userName, user[0].password, user[0].name, user[0].surname)
                return redirect("home")
        return render(request, "webstore/login.html")
    else:
        return render(request, "webstore/login.html")

def logout(request):
    global loggedUser
    loggedUser = None
    return render(request, "webstore/login.html")