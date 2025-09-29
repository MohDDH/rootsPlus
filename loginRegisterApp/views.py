from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt
from rootsPlusApp.models import User, Agronomist


def registerAccount(request, role):
    role = role.lower()
    model = None
    template = None

    
    if role == 'user':
        model = User
        template = 'registerUser.html'
    elif role == 'agronomist':
        model = Agronomist
        template = 'registerAgro.html'
    else:
        messages.error(request, "Invalid role.")
        return redirect('publicApp:home')

    if request.method == 'POST':
        
        errors = model.objects.register_validator(request.POST)
        if errors:
            for value in errors.values():
                messages.error(request, value)
            return redirect('loginRegisterApp:registerAccount', role=role)

        
        hashed_pw = bcrypt.hashpw(
            request.POST['password'].encode(),
            bcrypt.gensalt()
        ).decode()

        
        if role == 'user':
            account = model.objects.create(
                name=request.POST['name'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                city=request.POST['city'],
                password=hashed_pw
            )
        elif role == 'agronomist':
            account = model.objects.create(
                name=request.POST['name'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                city=request.POST['city'],
                specialization=request.POST['specialization'],
                password=hashed_pw
            )

        
        request.session[f'{role}_id'] = account.id
        request.session[f'{role}_name'] = account.name
        request.session['role'] = role

        messages.success(request, f"Welcome {account.name}, your account has been created.")
        return redirect('rootsPlusApp:dashboard')

    
    current_role = request.session.get('role', 'guest')
    return render(request, template, {'role': current_role})



def loginAccount(request, role):
    role = role.lower()
    model = None
    template = None

    if role == 'user':
        model = User
        template = 'loginUser.html' 
    elif role == 'agronomist':
        model = Agronomist
        template = 'loginAgro.html' 
    else:
        messages.error(request, "Invalid role.")
        return redirect('publicApp:home') 

    if request.method == 'POST':
        errors = model.objects.login_validator(request.POST)
        if errors:
            for value in errors.values():
                messages.error(request, value)
            return redirect('loginRegisterApp:loginAccount', role=role)

        account = model.objects.filter(email=request.POST['email']).first()
        if not account:
            messages.error(request, "Invalid login attempt.")
            return redirect('loginRegisterApp:loginAccount', role=role)

        if not bcrypt.checkpw(request.POST['password'].encode(), account.password.encode()):
            messages.error(request, "Invalid login attempt.")
            return redirect('loginRegisterApp:loginAccount', role=role)

       
        request.session[f'{role}_id'] = account.id
        request.session[f'{role}_name'] = account.name
        request.session['role'] = role

        messages.success(request, f"Welcome {account.name}")
        return redirect('rootsPlusApp:dashboard')

    
    current_role = request.session.get('role', 'guest')
    return render(request, template, {'role': current_role})

def logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('loginRegisterApp:loginAccount', role='user')