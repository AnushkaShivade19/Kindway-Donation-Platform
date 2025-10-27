from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import DonorRegistrationForm, NGORegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


def register_donor(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Donor account created successfully!')
            return redirect('login')
    else:
        form = DonorRegistrationForm()
    return render(request, 'accounts/register_donor.html', {'form': form})


def register_ngo(request):
    if request.method == 'POST':
        form = NGORegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'NGO account created successfully!')
            return redirect('login')
    else:
        form = NGORegistrationForm()
    return render(request, 'accounts/register_ngo.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'donor':
                    return redirect('donor_dashboard')
                elif user.role == 'ngo':
                    return redirect('ngo_dashboard')
                else:
                    return redirect('/')
            else:
                messages.error(request, 'Invalid credentials!')
        else:
            messages.error(request, 'Invalid credentials!')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('home')
