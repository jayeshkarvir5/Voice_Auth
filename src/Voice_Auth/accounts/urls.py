from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserLoginForm
from django.contrib.auth import logout

app_name = 'accounts'
urlpatterns = [
    path('get-started/', views.RegisterView.as_view(), name="register"),
    # path('login/<username>', LoginView.as_view(template_name="registration/login.html"
    # authentication_form=UserLoginForm), name="login"),
    path('login/<username>', views.LoginView.as_view(), name="login"),
    path('enter/', views.UnView.as_view(), name="enter-un"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('logout-page/', views.LogoutPage.as_view(), name="logout_page"),
]
