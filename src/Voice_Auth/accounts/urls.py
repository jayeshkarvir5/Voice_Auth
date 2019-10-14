from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from .forms import UserLoginForm

app_name = 'accounts'
urlpatterns = [
    path('get-started/', views.RegisterView.as_view(), name="register"),
    # path('login/<username>', LoginView.as_view(template_name="registration/login.html",
    # authentication_form=UserLoginForm), name="login"),
    path('login/<username>', views.LoginView.as_view(), name="login"),
    path('index/', views.IndexView.as_view(), name="index"),
    path('enter/', views.UnView.as_view(), name="enter-usr"),
    path('logout/', views.LogoutView, name="logout"),
    path('logout-page/', views.LogoutPage.as_view(), name="logout_page"),
]
