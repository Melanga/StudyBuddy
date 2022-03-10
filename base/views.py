from django.shortcuts import render, redirect
from .models import Room, Topic
from .forms import RoomForm


def home(request):
    # get q value in url to filter out the topic
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    rooms = Room.objects.filter(topic__name__icontains=q)
    topics = Topic.objects.all()
    context = {'rooms': rooms, 'topics': topics}
    return render(request, 'base/home.html', context)


def room(request, pk):
    selected_room = Room.objects.get(id=pk)
    context = {'room': selected_room}
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
    selected_room = Room.objects.get(id=pk)
    # pre-fill the form using room data
    form = RoomForm(instance=selected_room)

    if request.method == "POST":
        # instance is defined to update the existing data instead of creating new one
        form = RoomForm(request.POST, instance=selected_room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


def delete_room(request, pk):
    selected_room = Room.objects.get(id=pk)
    if request.method == "POST":
        selected_room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': selected_room})
