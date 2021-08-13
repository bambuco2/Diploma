from webstore.views import views
from django.urls.conf import path

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("products/", views.products, name="products"),
]