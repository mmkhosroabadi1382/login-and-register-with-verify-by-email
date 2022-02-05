from django.shortcuts import render, redirect
from account.models import Profile
from django.contrib.auth.models import User
from django.contrib import messages
from account.models import *
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required


@login_required(login_url="/")
def home(request):
    return render(request, 'home.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        passworld = request.POST.get('passworld')
        use_obj = User.objects.filter(username = username).first()
        if use_obj is None:
            messages.success(request, 'user not found.')
            return redirect('/login')
        profile_obj = Profile.objects.filter(user = use_obj).first()
        if not profile_obj.is_verified:
            messages.success(request, 'profile is not verified check your mail')
            return redirect('/login')
        user = authenticate(username = username, passworld = passworld)
        if user is None:
            messages.success(request, 'wrong passworld.')
            return redirect('/login')
        login(request,user)
        return redirect('/')
    return render(request, 'login.html')

def register(request):
    try:
        if request.method=='POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            passworld = request.POST.get('passworld')
            if User.objects.filter(username = username).first():
                messages.success(request, 'username is taken.')
                return redirect('/register')
            if User.objects.filter(email = email).first():
                messages.success(request, 'email is taken.')
                return redirect('/register')
            user_obj = User(username = username, email = email)
            user_obj.set_password(passworld)
            user_obj.save()
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user = user_obj , token = auth_token )
            profile_obj.save()
            send_mail_after_registeration(email, auth_token)
            return redirect('/token')
    except Exception as e:
        print(e)
    return render(request, 'register.html')

def success(request):
    return render(request, 'success.html')

def token_send(request):
    return render(request, 'token_send.html')

def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token = auth_token).first()
        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'your account is already verified')
                return redirect('/login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'your account has been verified')
            return redirect('/login')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)

def error_page(request):
    return render(request, 'error.html')

def send_mail_after_registeration(email, token):
    subject = 'your account need to be verifid'
    message = f'hi paste the link to verify your account http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message ,email_from, recipient_list)