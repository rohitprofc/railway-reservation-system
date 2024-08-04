from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .models import trains, person


def index(request):
    lis = trains.objects.all()
    return render(request, './viewtrains.html', {"lis": lis})


def loginform(request):
    return render(request, './login.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['name']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            context = {'msg': "Error: User is not registered/invalid"}
            return render(request, './error.html', context)
    return redirect('loginform')


def registerform(request):
    return render(request, './register.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username, email, password)
        user.save()
        context = {'msg': "Registration Successful"}
        return render(request, './error.html', context)
    return redirect('registerform')


def logout(request):
    auth_logout(request)
    context = {'msg': "Logout Successful"}
    return render(request, './error.html', context)


@login_required
def trainform(request):
    if request.user.is_superuser:
        return render(request, './addtrain.html')
    else:
        return render(request, './error.html', {'msg': "Not an Admin"})


@login_required
def addtrain(request):
    if request.method == 'POST':
        l = trains(
            source=request.POST['source'],
            destination=request.POST['destination'],
            time=request.POST['time'],
            seats_available=request.POST['seats_available'],
            train_name=request.POST['train_name'],
            price=request.POST['price']
        )
        l.save()
        return render(request, './error.html', {'msg': "Successfully Added"})
    return redirect('trainform')


@login_required
def train_id(request, train_id):
    if request.user.is_superuser:
        train = trains.objects.get(pk=train_id)
        persons = train.person_set.all()
        context = {
            'train': train,
            'persons': persons
        }
        return render(request, './viewperson.html', context)
    else:
        return render(request, './error.html', {'msg': "Not an Admin"})


@login_required
def book(request):
    if request.method == 'POST':
        source = request.POST['source']
        destination = request.POST['destination']
        name = request.POST['name']
        age = request.POST['age']
        gender = request.POST['gender']

        trains_queryset = trains.objects.filter(source=source, destination=destination)
        if trains_queryset.exists():
            request.session['booking_info'] = {
                'name': name,
                'age': age,
                'gender': gender
            }
            return render(request, './trainsavailable.html', {'trains': trains_queryset})
        else:
            return render(request, './error.html', {'msg': "No trains found for the selected route."})
    return redirect('bookform')


@login_required
def booking(request, train_id):
    booking_info = request.session.get('booking_info')
    if not booking_info:
        return render(request, './error.html', {'msg': "No booking information found."})

    train = trains.objects.get(pk=train_id)
    if train.seats_available == 0:
        return render(request, './error.html', {'msg': "Seats full"})
    
    train.seats_available -= 1
    train.save()

    person_instance = person(
        train=train,
        name=booking_info['name'],
        email=request.user.email,
        age=booking_info['age'],
        gender=booking_info['gender']
    )
    person_instance.save()

    return render(request, './error.html', {'msg': f"Booked Successfully. Price to be paid is {train.price}"})


@login_required
def bookform(request):
    trains_queryset = trains.objects.all()
    sources = list(set(train.source for train in trains_queryset))
    destinations = list(set(train.destination for train in trains_queryset))

    return render(request, './booking.html', {'sources': sources, 'destinations': destinations})


@login_required
def mybooking(request):
    booked_persons = person.objects.filter(email=request.user.email)
    return render(request, './mybooking.html', {'persons': booked_persons})
