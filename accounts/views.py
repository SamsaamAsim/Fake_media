# from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from .forms import RegisterForm, LoginForm, ResetForm,ForgotPasswordForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
# from store.views import _cartid
# from store.models import CartModel,CartItemModel
import requests
from django.shortcuts import get_object_or_404
from .models import UserProfile



# email avtivation
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings

from .forms import UserForm, UserProfileForm

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Process the valid form data and create a user
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.phone_number = phone_number
            user.save()
            
            #user email activation
            current_site=get_current_site(request)
            mail_subject="Ai detection account activation link"
            message=render_to_string("accounts/email_verification.html",{
                "user":user,
                "domain":current_site,
                "uid":urlsafe_base64_encode(force_bytes(user.pk)),
                "token":default_token_generator.make_token(user)
            })
            email_to=[email]
            email_from=settings.EMAIL_HOST_USER
            send_email=EmailMessage(mail_subject,message,email_from,email_to)
            
            send_email.send()
            
            messages.success(request, f"Verification email has been sent to {email} please verify through your email")
            
            # Redirect to a success page or login page, for example
            return redirect('login')  # Replace with your desired URL

    else:
        form = RegisterForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data["email"]
            user_password = form.cleaned_data["password"]
            user = auth.authenticate(email=user_email, password=user_password)
            print(f"user is this {user}")
            if user is not None:
                auth.login(request, user)
                messages.success(request, "You are logged in successfully")
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    parms = dict(x.split('=') for x in query.split('&'))
                    if 'next' in parms:
                        nextpage = parms['next']
                        return redirect(nextpage)
                except:
                    print("world")
                    return redirect("/")  # Redirect to a default page if 'next' is not present
            else:
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Invalid form data")
    else:
        form = LoginForm()

    context = {"form": form}
    return render(request, "accounts/signin.html", context)




@login_required(login_url="login")
def logout_view(request):
    logout(request)
    messages.success(request, "logout successfully")

    return redirect('login')  



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated. You can now log in.')
        return redirect('login')  # Redirect to the login page
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('login')  # Redirect to the login page with an error message




def forgot_password(request):
    form = LoginForm()

    if request.method == "POST":
        form = ResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data["email"]
            if Account.objects.filter(email=user_email).exists():
                user = Account.objects.get(email=user_email)

                # User email activation
                current_site = get_current_site(request)
                mail_subject = "ecommerce account password reset link"
                message = render_to_string("accounts/password_reset.html", {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user)
                })
                email_to = [user_email]
                email_from = settings.EMAIL_HOST_USER
                send_email = EmailMessage(mail_subject, message, email_from, email_to)

                send_email.send()
                messages.success(request, f"Password reset email has been sent to {user_email}. Please reset your password through email.")
                
                # Redirect to a success page or login page, for example
                return redirect('login')  # Replace with your desired URL
            else:
                messages.error(request, "Email does not exist.")
        else:
            messages.error(request, "Invalid information.")
    context = {"form": form}
    return render(request, "accounts/forgot_password.html", context)



def forgotpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request, 'please reset you password')
        return redirect("resetpassword")
    else:
        messages.error(request, 'link expired')
        return redirect("login")



def reset_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]
            if password==confirm_password:
                uid=request.session.get("uid")
                user=Account.objects.get(pk=uid)
                user.set_password(password)
                user.save()
            else:
                messages.error(request, 'Passwords do not match')
                return redirect("resetpassword")
                
            messages.success(request, 'Your password has reset successfully.')
            return redirect('login')  # Redirect to the login page after resetting the password
        else:
            messages.error(request, 'Invalid form data.')
    else:
        form = ForgotPasswordForm()
    context={"form":form}
    return render(request, "accounts/reset_password_form.html", context)

# @receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)    

@login_required(login_url="login")
def edit_profile(request):
    user = request.user
    userprofile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated")
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=userprofile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    
    return render(request, 'accounts/edit_profile.html', context)