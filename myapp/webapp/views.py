from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from .forms import RegistrationForm #LoginForm
# from django_otp import devices_for_user, match_token
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.utils import timezone
from .models import LoginAttempt
from datetime import timedelta
import time
import random
# from django_otp.plugins.otp_totp.models import TOTPDevice
# import qrcode
# from io import BytesIO

# def custom_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
        
#         if user is not None:
#             # Check if user has 2FA enabled
#             devices = list(devices_for_user(user))
#             if devices:
#                 # Store user in session for 2FA step
#                 request.session['pre_2fa_user_id'] = user.id
#                 return redirect('../verify-2fa/')
#             else:
#                 login(request, user)
#                 return redirect('/')
#         else:
#             return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
#     return render(request, 'accounts/login.html')

# def custom_login(request):
#     if request.method == 'POST':
#         form = LoginForm(data=request.POST)
#         if form.is_valid():  # This checks CAPTCHA too
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 if not user.email:
#                     return render(request, 'accounts/login.html', {'form': form, 'error': 'No email registered'})
#                 code = str(random.randint(100000, 999999))
#                 request.session['2fa_code'] = code
#                 request.session['pre_2fa_user_id'] = user.id
#                 try:
#                     send_mail(
#                         'Your 2FA Code',
#                         f'Your verification code is: {code}',
#                         'your-email@gmail.com',  # Replace with EMAIL_HOST_USER
#                         [user.email],
#                         fail_silently=False,
#                     )
#                 except Exception as e:
#                     return render(request, 'accounts/login.html', {'form': form, 'error': f'Email failed: {str(e)}'})
#                 return redirect('verify_2fa')
#             else:
#                 return render(request, 'accounts/login.html', {'form': form, 'error': 'Invalid credentials'})
#         else:
#             return render(request, 'accounts/login.html', {'form': form, 'error': 'CAPTCHA validation failed'})
#     else:
#         form = LoginForm()
#     return render(request, 'accounts/login.html', {'form': form})

def custom_login(request):
    ip = request.META.get('REMOTE_ADDR', 'unknown_ip')  # Get client IP
    attempt_key = f'login_attempts_{ip}'  # Unique key per IP
    lockout_key = f'login_lockout_{ip}'
    max_attempts = 4
    lockout_seconds = 30

    if request.session.get(lockout_key):
        time_remaining = request.session[lockout_key] - int(time.time())
        if time_remaining > 0:
            return render(request, 'accounts/login.html', {
                'error': f'Too many failed attempts from this IP. Wait {time_remaining} seconds.'
            })
        else:
            # Lockout expired, reset
            del request.session[lockout_key]
            request.session[attempt_key] = 0

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            request.session[attempt_key] = 0
            if not user.email:
                return render(request, 'accounts/login.html', {'error': 'No email registered'})
            code = str(random.randint(100000, 999999))
            request.session['2fa_code'] = code
            request.session['pre_2fa_user_id'] = user.id
            try:
                send_mail(
                    'Your 2FA Code',
                    f'Your verification code is: {code}',
                    'from@example.com',  # Replace with EMAIL_HOST_USER
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                return render(request, 'accounts/login.html', {'error': f'Email failed: {str(e)}'})
            return redirect('verify_2fa')
        else:
            attempts = request.session.get(attempt_key, 0) + 1
            request.session[attempt_key] = attempts
            if attempts >= max_attempts:
                request.session[lockout_key] = int(time.time()) + lockout_seconds
                return render(request, 'accounts/login.html', {
                    'error': f'Too many failed attempts from this IP. Wait {lockout_seconds} seconds.'
                })
            return render(request, 'accounts/login.html', {
                'error': f'Invalid credentials. Attempt {attempts} of {max_attempts} from this IP.'
            })
    return render(request, 'accounts/login.html')

def verify_2fa(request):
    if request.method == 'POST':
        entered_code = request.POST.get('code')
        stored_code = request.session.get('2fa_code')
        user_id = request.session.get('pre_2fa_user_id')
        if user_id and entered_code == stored_code:
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            login(request, user)
            del request.session['2fa_code']
            del request.session['pre_2fa_user_id']
            return redirect('/result')
        else:
            return render(request, 'accounts/verify2fa.html', {'error': 'Invalid code'})
    return render(request, 'accounts/verify2fa.html')

def result(request):
    return render(request, 'accounts/result.html')  # This is the page that will be shown

def webapp(request):
  template = loader.get_template('accounts/myfirst.html')
  return HttpResponse(template.render())    

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('/')  # Redirect to homepage
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

# def verify_2fa(request):
#     if request.method == 'POST':
#         token = request.POST.get('token')
#         user_id = request.session.get('pre_2fa_user_id')
#         if user_id:
#             from django.contrib.auth.models import User
#             user = User.objects.get(id=user_id)
#             if match_token(user, token):
#                 login(request, user)
#                 del request.session['pre_2fa_user_id']  # Clean up
#                 return redirect('/')
#             else:
#                 return render(request, 'accounts/verify2fa.html', {'error': 'Invalid 2FA code'})
#     return render(request, 'accounts/verify2fa.html')

# @login_required
# def setup_2fa(request):
#     if request.method == 'POST':
#         device = TOTPDevice.objects.create(user=request.user, name='default', confirmed=True)
#         return redirect('/')
#     else:
#         # Check if user already has a device
#         if list(devices_for_user(request.user)):
#             return redirect('/')
        
#         # Create a temporary device to generate QR code
#         device = TOTPDevice(user=request.user, name='default')
#         qr_url = device.config_url  # URL for authenticator app
        
#         # Generate QR code
#         qr = qrcode.make(qr_url)
#         buffer = BytesIO()
#         qr.save(buffer, format="PNG")
#         qr_image = b64encode(buffer.getvalue()).decode('utf-8')
        
#         return render(request, 'accounts/setup2fa.html', {'qr_image': qr_image})