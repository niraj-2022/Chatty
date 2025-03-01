from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.http import HttpResponse
from .models import Connections, ChatMsg
from django.db.models import Q


def index(request):
    if request.user.is_authenticated:
        frnd_username = request.GET.get('name', None)
        me = request.user.username

        chats, friend_name = None, None
        if frnd_username:
            chats = ChatMsg.objects.filter(Q(sender=me, receiver=frnd_username) | Q(
                sender=frnd_username, receiver=me)).order_by('msg_id')
            friend_tuple = User.objects.filter(username=frnd_username).first()
            friend_name = friend_tuple.first_name + " " + friend_tuple.last_name

        friends_list = Connections.objects.filter(me=me).values_list('friend')
        friends_data = User.objects.filter(username__in=friends_list)
        data = {"friends": friends_data,
                "frnd_name": friend_name, "frnd_username": frnd_username, "chats": chats}

        return render(request, 'index.html', data)
    return render(request, 'auth.html')


def login(request):
    if request.method == "GET":
        return redirect('/')

    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username, password=password)

    if user:
        auth.login(request, user)
        print(f"*******[LOGIN: {username}]*******")
        return redirect('/')
    else:
        messages.error(request, "Invalid credentials")
        return redirect('login')


def register(request):
    if request.method == "GET":
        return redirect('/')

    first_name = request.POST['first_name']
    last_name = request.POST['last_name']
    username = request.POST['username']
    email = request.POST['email']
    password1 = request.POST['password1']
    password2 = request.POST['password2']

    if password1 != password2:
        messages.error(request, "Password not matching")
        return redirect('register')

    if User.objects.filter(username=username).exists():
        messages.error(request, "Username Taken")
        return redirect('register')

    if User.objects.filter(email=email).exists():
        messages.error(request, "Email Taken")
        return redirect('register')

    user = User.objects.create_user(
        first_name=first_name, last_name=last_name, username=username, email=email, password=password1)

    print(f"*******[REGISTER: {user}]*******")
    return redirect('/')


def logout(request):
    print(f"*******[LOGOUT: {request.user}]*******")
    auth.logout(request)
    return redirect('/')


def add_friend(request):
    if request.method == 'POST':
        friend = request.POST['friend']
        me = request.user.username

        if User.objects.filter(username=friend).exists() and friend != me:
            if not Connections.objects.filter(me=me, friend=friend).exists():
                Connections.objects.create(me=me, friend=friend)
                Connections.objects.create(me=friend, friend=me)

    return HttpResponse('')
