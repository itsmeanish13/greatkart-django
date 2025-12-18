from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages as message
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
#verification email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string #for rendering email templates
from django.utils.http import urlsafe_base64_encode #to encode user ids
from django.utils.encoding import force_bytes #to convert user ids to bytes
from django.contrib.auth.tokens import default_token_generator #to generate tokens
from django.core.mail import EmailMessage #to send emails 
from django.utils.http import urlsafe_base64_decode #to decode user ids


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
            
            
            #user activation email can be sent here
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                
            })
            to_email = email    #recipient email address
            send_email = EmailMessage(mail_subject, message, to=[to_email])    
            send_email.send()
            
            
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
@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    message.success(request, 'You have been logged out successfully!')
    return redirect('login')
def activate(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64).decode())
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        message.success(request, 'Congratulations! Your account has been activated.')
        return redirect('login')
    else:
        message.error(request, 'Invalid activation link')
        return redirect('register')
    