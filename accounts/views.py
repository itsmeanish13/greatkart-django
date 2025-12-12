from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages as message
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.phone_number = phone_number
            
            
            
            user.save()
            message.success(request, 'Your account has been registered successfully!')
            return redirect('register')
            
    else:
        form = RegistrationForm()
        
    context = {'form': form}
    
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Use username=email if your custom user model uses email
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            message.success(request, 'You have been logged in successfully!')
            return redirect('home')
        else:
            message.error(request, 'Invalid email or password.')
            return redirect('login')
    
    # GET request, just render login page
    return render(request, 'accounts/login.html')
def logout(request):
    auth_logout(request)
    message.success(request, 'You have been logged out successfully!')
    return redirect('login')
