from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy
from myauth.views import (
    set_cookie_view,
    get_cookie_view,
    set_session_view,
    get_session_view,
    MyLogoutView,
    AboutMeView,
    RegisterView,
    FooBarView, HelloView,
)

app_name = "myauth"

urlpatterns = [

    path("login/",
         LoginView.as_view(
             template_name= "myauth/login.html",
             redirect_authenticated_user = True,
         ),
         name="login"
    ),
    # path("logout/", logout_view, name="logout"),
    path("logout/",
         MyLogoutView.as_view(),
         name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("register/", RegisterView.as_view(), name="register"),

    path("cookie/set/", set_cookie_view, name="cookie-set"),
    path("cookie/get/", get_cookie_view, name="cookie-get"),

    path("session/get/", get_session_view, name="session-get"),
    path("session/set/", set_session_view, name="session-set"),
    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),
    path("hello/", HelloView.as_view(), name="hello"),
]