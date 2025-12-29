from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegistrationForm, CustomUserForm
from django.utils import timezone


def register_view(request):
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            response = redirect('inventory:products')
            response.set_cookie('registration_time', timezone.now().isoformat(), max_age=10*365*24*60*60)
            return response
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile has been updated successfully')
        else:
            messages.error(request, 'Please correct errors')
    else:
        form = CustomUserForm(instance=request.user)
    reg_cookie = request.COOKIES.get('registration_time')
    registered_at = None
    if reg_cookie:
        try:
            from datetime import datetime
            registered_at = datetime.fromisoformat(reg_cookie)
        except Exception:
            registered_at = reg_cookie

    return render(request, 'users/profile.html', {'form': form, 'registered_at': registered_at})