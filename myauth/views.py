from django.contrib.auth.forms import UserCreationForm
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Profile


class HelloView(View):
    def get(self, request:HttpRequest) -> HttpResponse:
        welcome_message = _("Hello World!")
        return HttpResponse(f"<h1>{welcome_message}</h1>")


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"


class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True,
                             max_length=254,
                             help_text=_('Required')
            )
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class RegisterView(CreateView):
    form_class = MyUserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form)->HttpResponse:
        response = super().form_valid(form)

        self.object.email = form.cleaned_data.get('email')
        self.object.save(update_fields=['email'])

        Profile.objects.create(user=self.object)

        password = form.cleaned_data.get('password1')

        user = authenticate(self.request,
                            username=self.object.username,
                            password=password)
        if user is not None:
            login(self.request, user=user)
        return response

def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/admin/')
        return render(request, 'myauth/login.html')
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin/')
    return render(request,
                  'myauth/login.html',
                  {'error': 'Invalid username or password'},
                  status=403)

class MyLogoutView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        logout(request)
        return redirect('myauth:login')

def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse('myauth:login'))

def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set:')
    response.set_cookie("fizz", "buzz", max_age=86400)
    return response

def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default_value")
    return HttpResponse(f"Cookie value: {value!r}")

def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set")

def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default_value")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
