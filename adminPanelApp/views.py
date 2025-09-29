# adminPanelApp/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from rootsPlusApp.models import User, Agronomist, Farm, Activity, Evaluation, FarmReport,Crop
from django.contrib.auth import authenticate, login, logout



def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and user.is_superuser:  
            login(request, user)
            request.session['role'] = 'admin'
            messages.success(request, f"Welcome {user.username}")
            return redirect('adminPanelApp:adminDashboard')
        else:
            messages.error(request, "Invalid admin credentials.")

    return render(request, 'adminLogin.html')

def adminDashboard(request):
    if request.session.get('role') != 'admin':
        messages.error(request, "Unauthorized access.")
        return redirect('adminPanelApp:adminLogin')

    users = User.objects.all()
    agronomists = Agronomist.objects.all()
    farms = Farm.objects.all()
    crops = Crop.objects.all()
    activities = Activity.objects.select_related('crop', 'agronomist').order_by('-date')[:10]
    evaluations = Evaluation.objects.select_related('farm', 'agronomist').order_by('-created_at')[:10]
    reports = FarmReport.objects.select_related('farm', 'author').order_by('-generated_at')[:10]

    stats = {
     'users_count': len(users),
    'agronomists_count': len(agronomists),
    'farms_count': len(farms),
    'crops_count': len(crops),
    'activities_count': Activity.objects.count(),
    'evaluations_count': Evaluation.objects.count(),
    'reports_count': FarmReport.objects.count(),
}

    return render(request, 'adminDashboard.html', {
        'users': users,
        'agronomists': agronomists,
        'farms': farms,
        'crops': crops,
        'activities': activities,
        'evaluations': evaluations,
        'reports': reports,
        'stats': stats,

    })


