from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from users.registermail import notify_user

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            lastname = form.cleaned_data.get('last_name')
            firstname = form.cleaned_data.get('first_name')
            msg = "Hello " + firstname +" "+lastname+ ",\n\nYour StockUp account has been successfully created. Welcome aboard! "\
                             "You can now login to the application and make use of all the services provided to you.\n\n" \
                             "Thank you,\nStockUp Team"

            notify_user(email,msg)
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request,'users/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'users/profile.html')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('logout')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form })
