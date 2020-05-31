from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
      first_name = request.POST['first_name']
      last_name = request.POST['last_name']
      username = request.POST['username']
      email = request.POST['email']
      password = request.POST['password']
      password2 = request.POST['password2']
      # check if password match
      if password == password2:
         # check username
         if User.objects.filter(username=username).exists():
            messages.error(request, 'Nazwa użytkownika jest zajęta')
            return redirect('register')
         else:
            if User.objects.filter(email=email).exists():
               messages.error(request, 'Email jest zajęty')
               return redirect('register')
            else:
               user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
               user.save()
               messages.success(request, 'Pomyślnie zarejestrowano')
               auth.login(request,user)
               return redirect('login')
      else:
         #message
         messages.error(request, 'Hasła nie są identyczne')
         return redirect('register')
    else:    
        return render(request, 'sockets/register.html')

def login(request):
   if request.method == 'POST':
      # login user
      username = request.POST['username']
      password = request.POST['password']
      user = auth.authenticate(username=username, password=password)
      if user is not None:
         auth.login(request, user)
         messages.success(request, 'Pomyślnie zalogowano')
         return redirect('index')
      else:
         messages.error(request, 'Podano niewłaściwe dane')
         return redirect('login')
   else:    
      return render(request, 'sockets/login.html')

def logout(request):
   if request.method == 'POST':
      auth.logout(request)
      messages.success(request, 'Wylogowano')
      return redirect('index')

@login_required(login_url='login')
def index(request):
    return render(request, 'sockets/index.html')

@login_required(login_url='login')
def room(request, room_name):
    return render(request, 'sockets/room.html', {
        'room_name': room_name
    })