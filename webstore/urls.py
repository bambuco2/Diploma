from webstore.views import views
from django.urls.conf import path

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login, name="login"),
]