from django.shortcuts import render

rooms = [
    {'id': 1, 'name': 'lets learn python'},
    {'id': 2, 'name': 'Design with me'},
    {'id': 3, 'name': 'Frontend developers'}
]


def home(request):
    context = {'rooms': rooms}
    return render(request, 'base/home.html', context)


def room(request, pk):
    context = {'room': i for i in rooms if i['id'] == int(pk)}
    return render(request, 'base/room.html', context)
