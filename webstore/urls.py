from webstore.views import views
from django.urls.conf import path

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("products/", views.products, name="products"),
    path("household-appliances/", views.products, name="household-appliances"),
    path("fashion/", views.products, name="fashion"),
    path("fitness/", views.products, name="fitness"),
    path("audio-video/", views.products, name="audio-video"),
    path("yard-tools/", views.products, name="yard-tools"),
]