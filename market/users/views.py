from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegistrationForm, CustomUserForm


def register_view(request):
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            return redirect('inventory:products')
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
    return render(request, 'users/profile.html', {'form': form})