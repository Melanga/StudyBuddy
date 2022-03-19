from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, ModifiedUserCreationForm


def login_page(request):
    page = 'login'
    # if user is already logged in redirected to home instead of going to login page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Enter correct username or password")

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def register_user(request):
    form = ModifiedUserCreationForm()
    if request.method == "POST":
        form = ModifiedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
    return render(request, 'base/login_register.html', {'form': form})


@login_required(login_url='login')
def update_user(request):
    selected_user = request.user
    form = UserForm(instance=selected_user)
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=selected_user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=selected_user.id)
    return render(request, 'base/update_user.html', {'form': form})


def home(request):
    # get q value in url to filter out the topic
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    recent_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )[0:3]
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'recent_messages': recent_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    selected_room = Room.objects.get(id=pk)
    room_messages = selected_room.message_set.all().order_by('-created')
    participants = selected_room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=selected_room,
            body=request.POST.get('body')
        )
        selected_room.participants.add(request.user)
        return redirect('room', pk=selected_room.id)
    context = {'room': selected_room, 'messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


def user_profile(request, pk):
    selected_user = User.objects.get(id=pk)
    rooms = selected_user.room_set.all()
    recent_messages = selected_user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': selected_user, 'rooms': rooms, 'recent_messages': recent_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('Only host can edit room attributes...')
    if request.method == "POST":
        message.delete()
        return redirect('room', pk=message.room.id)
    return render(request, 'base/delete.html', {'obj': message})


# if user is not logged in, user is redirected to login page when create room request
@login_required(login_url='login')
def create_room(request):
    form = RoomForm
    topics = Topic.objects.all()
    # POST method is defined in room_form.html as form submission and http request come from same address as from url,
    # so we need to check if it is form submission or page request and is it is a POST request from form,
    # we need to handle it instead of rendering the html content.
    if request.method == "POST":
        # to access data and manually validate if you want
        # request.POST.get('name')
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     selected_room = form.save(commit=False)
        #     selected_room.host = request.user
        #     selected_room.save()
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    # get room object data from id
    selected_room = Room.objects.get(id=pk)
    # pre-fill the form using room data
    form = RoomForm(instance=selected_room)
    topics = Topic.objects.all()

    if request.user != selected_room.host:
        return HttpResponse('Only host can edit room attributes...')

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        # instance is defined to update the existing data instead of creating new one
        selected_room.name = request.POST.get('name')
        selected_room.topic = topic
        selected_room.description = request.POST.get('description')
        selected_room.save()
        # form = RoomForm(request.POST, instance=selected_room)
        # if form.is_valid():
        #     form.save()
        return redirect('home')
    context = {'form': form, 'topics': topics, 'room': selected_room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def delete_room(request, pk):
    selected_room = Room.objects.get(id=pk)

    if request.user != selected_room.host:
        return HttpResponse('Only host can edit room attributes...')

    if request.method == "POST":
        selected_room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': selected_room})


def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    room_count = Room.objects.all().count()
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics, 'room_count': room_count})


def activity_page(request):
    recent_messages = Message.objects.all()[0:50]
    return render(request, 'base/activity.html', {'messages': recent_messages})
