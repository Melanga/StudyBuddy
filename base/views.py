from django.shortcuts import render, redirect
from .models import Room
from .forms import RoomForm


def home(request):
    rooms = Room.objects.all()
    context = {'rooms': rooms}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room': room}
    return render(request, 'base/room.html', context)


def create_room(request):
    form = RoomForm
    # POST method is defined in room_form.html as form submission and http request come from same address as from url,
    # so we need to check if it is form submission or page request and is it is a POST request from form,
    # we need to handle it instead of rendering the html content.
    if request.method == "POST":
        # to access data and manually validate if you want
        # request.POST.get('name')
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


def update_room(request, pk):
    # get room object data from id
    room = Room.objects.get(id=pk)
    # pre-fill the form using room data
    form = RoomForm(instance=room)

    if request.method == "POST":
        # instance is defined to update the existing data instead of creating new one
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)
