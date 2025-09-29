from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Farm, User, Agronomist,FarmReport, Evaluation, Analysis, Activity, Crop
from django.shortcuts import render
from django.db.models import Avg, Max
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.http import JsonResponse, HttpResponseForbidden
import requests
from datetime import datetime, timedelta
from django.http import HttpResponse
import csv



# ----- Dashboard -----
def dashboard(request):

    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')

    role = request.session.get('role', 'guest')
    userName = request.session.get(f'{role}_name', 'Guest')
    userID = request.session.get(f'{role}_id')

    context = {
        'role': role,
        'userName': userName,
        'userID': userID
    }

    farms = []
    latest_evaluations = []
    latest_reports = []

    if role in ['farmer', 'user']:
        try:
            current_user = User.objects.get(id=userID)
            farms = current_user.farms.all()

            
            latest_evaluations = Evaluation.objects.filter(
                farm__in=farms
            ).order_by('-created_at')[:2]

            
            latest_reports = FarmReport.objects.filter(
                farm__in=farms
            ).order_by('-generated_at')[:2]

            
            farms_count = farms.count()

            
            total_crops = sum(farm.get_crops_count() for farm in farms)

            
            avg_yield_per_dunum = 0
            if farms_count > 0:
                avg_yield_per_dunum = sum(
                    farm.get_average_yield_per_dunum() or 0 for farm in farms
                ) / farms_count

            # Data for Charts
            farm_names = [farm.name for farm in farms]
            crops_counts = [farm.get_crops_count() for farm in farms]
            total_yields = [farm.get_total_farm_yield() or 0 for farm in farms]
            avg_yields = [farm.get_average_yield_per_dunum() or 0 for farm in farms]

            context.update({
                # KPIs
                'farms_count': farms_count,
                'total_crops': total_crops,
                'avg_yield_per_dunum': round(avg_yield_per_dunum, 2),

                
                'farm_names': json.dumps(farm_names, cls=DjangoJSONEncoder),
                'crops_counts': json.dumps(crops_counts, cls=DjangoJSONEncoder),
                'total_yields': json.dumps(total_yields, cls=DjangoJSONEncoder),
                'avg_yields': json.dumps(avg_yields, cls=DjangoJSONEncoder),

                # For Each Farm
                'farm_data': [
                    {
                        'name': farm.name,
                        'crops_count': farm.get_crops_count(),
                        'total_yield': farm.get_total_farm_yield() or 0,
                        'avg_yield': farm.get_average_yield_per_dunum() or 0
                    }
                    for farm in farms
                ]
            })

        except User.DoesNotExist:
            farms = []

    elif role == 'agronomist':
        try:
            current_agro = Agronomist.objects.get(id=userID)
            farms = current_agro.managed_farms.all()

            # KPI
            total_farms = farms.count()
            evaluations = Evaluation.objects.filter(farm__in=farms, agronomist=current_agro)
            total_evaluations = evaluations.count()
            avg_score = evaluations.aggregate(avg=Avg('overall_score'))['avg'] or 0
            last_eval_date = evaluations.aggregate(last=Max('created_at'))['last']

            
            farm_names = [farm.name for farm in farms]
            crops_counts = [farm.get_crops_count() for farm in farms]
            avg_yields = [farm.get_average_yield_per_dunum() or 0 for farm in farms]
            total_crops = sum(crops_counts)

            # Bubble Chart Data
            bubble_data = []
            for farm in farms:
                activity_count = farm.activities.filter(agronomist=current_agro).count()
                evaluation_count = farm.evaluations.filter(agronomist=current_agro).count()
                report_count = farm.reports.filter(author=current_agro).count()

                bubble_data.append({
                    'label': farm.name,
                    'x': activity_count,
                    'y': evaluation_count,
                    'r': max(report_count * 5, 5) 
                })

            context.update({
                'bubble_data': json.dumps(bubble_data, cls=DjangoJSONEncoder)
            })

            context.update({
                'total_farms': total_farms,
                'total_evaluations': total_evaluations,
                'total_crops': total_crops,
                'avg_score': round(avg_score, 2),
                'last_eval_date': last_eval_date,
                'farm_names': json.dumps(farm_names, cls=DjangoJSONEncoder),
                'crops_counts': json.dumps(crops_counts, cls=DjangoJSONEncoder),
                'avg_yields': json.dumps(avg_yields, cls=DjangoJSONEncoder),
            })

            latest_evaluations = Evaluation.objects.filter(
                agronomist=current_agro
            ).order_by('-created_at')[:2]

            latest_reports = FarmReport.objects.filter(
                farm__in=farms
            ).order_by('-generated_at')[:2]

        except Agronomist.DoesNotExist:
            farms = []

    context.update({
        'farms': farms,
        'farms_count': farms.count(),
        'latest_evaluations': latest_evaluations,
        'latest_reports': latest_reports,
    })

    return render(request, 'dashboard.html', context)

# Farms
def add_farm(request):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')

    role = request.session.get('role', 'guest')
    farms_list = []
    farmers_list = []

   
    if role == 'agronomist' or request.user.is_superuser:
        farms_list = Farm.objects.all()
        farmers_list = User.objects.all()

    if request.method == 'POST':
        if role == 'agronomist' or request.user.is_superuser:
            agronomist_id = request.session.get('agronomist_id')
            agronomist = None
            if agronomist_id:
                agronomist = get_object_or_404(Agronomist, id=agronomist_id)

            existing_farm_id = request.POST.get('existing_farm')
            if existing_farm_id:
                farm = get_object_or_404(Farm, id=existing_farm_id)
                if agronomist:
                    farm.agronomists.add(agronomist)
                messages.success(request, f"You are now managing farm: {farm.name}")
                return redirect('rootsPlusApp:dashboard')
            else:
                owner_id = request.POST.get('owner_id')
                owner = get_object_or_404(User, id=owner_id)
                name = request.POST.get('name')
                location = request.POST.get('location')
                total_area = request.POST.get('total_area')

                if not name or not location or not total_area:
                    messages.error(request, "Please fill all required fields for new farm.")
                    return redirect('rootsPlusApp:add_farm')

                new_farm = Farm.objects.create(
                    name=name,
                    location=location,
                    total_area=total_area,
                    user=owner
                )
                if agronomist:
                    new_farm.agronomists.add(agronomist)
                messages.success(request, f"New farm '{new_farm.name}' created successfully.")
                return redirect('rootsPlusApp:add_crop_to_farm', farm_id=new_farm.id)

        elif role == 'user' or role == 'farmer':
            user_id = request.session.get('user_id')
            name = request.POST.get('name')
            location = request.POST.get('location')
            total_area = request.POST.get('total_area')

            if not name or not location or not total_area:
                messages.error(request, "Please fill all required fields.")
                return redirect('rootsPlusApp:add_farm')

            farm = Farm.objects.create(
                name=name,
                location=location,
                total_area=total_area,
                user_id=user_id
            )
            messages.success(request, "New farm created successfully.")
            print(farm.id, user_id, role)
            return redirect('rootsPlusApp:add_crop_to_farm', farm_id=farm.id)

        else:
            messages.error(request, "You are not authorized to add farms.")
            return redirect('publicApp:home')

    return render(request, 'addFarm.html', {
        'role': role,
        'farms_list': farms_list,
        'farmers_list': farmers_list
    })

def farm_detail(request, farm_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')
    farm = get_object_or_404(Farm, id=farm_id)
    analysis = farm.analyses.first()
    activities = farm.activities.order_by('-date')
    evaluations = farm.evaluations.order_by('-created_at')
    latest_eval = evaluations.first()

    
    crops = farm.crops.all()
    total_crop_area = sum([crop.crop_area for crop in crops if crop.crop_area])
    crop_data = []

    for crop in crops:
        percentage = (crop.crop_area / farm.total_area * 100) if farm.total_area else 0
        crop_data.append({
            'name': crop.crop_name,
            'area': crop.crop_area,
            'percentage': round(percentage, 2)
        })

    
    unplanted_area = max(farm.total_area - total_crop_area, 0)

    chart_labels = [crop.crop_name for crop in crops]
    chart_areas = [float(crop.crop_area) for crop in crops]

    if unplanted_area > 0:
        chart_labels.append("Unplanted Area")
        chart_areas.append(float(unplanted_area))

    crop_labels = json.dumps(chart_labels)
    crop_areas = json.dumps(chart_areas)

    
    if request.method == 'POST' and not analysis:
        soil_type = request.POST.get('soil_type')
        soil_salinity = request.POST.get('soil_salinity')
        soil_ph = request.POST.get('soil_ph')
        water_salinity = request.POST.get('water_salinity')
        analysis_date = request.POST.get('analysis_date')

        Analysis.objects.create(
            farm=farm,
            soil_type=soil_type,
            soil_salinity=soil_salinity or None,
            soil_ph=soil_ph or None,
            water_salinity=water_salinity or None,
            analysis_date=analysis_date or None
        )

        messages.success(request, "Farm analysis saved successfully.")
        return redirect('rootsPlusApp:farm_detail', farm_id=farm.id)

    latest_activities = farm.activities.select_related('crop').order_by('-date')[:3]
    latest_reports = farm.reports.order_by('-generated_at')[:3]

    crop_efficiency = []
    for crop in crops:
        yield_per_dunum = crop.yield_per_dunum or 0
        activity_count = crop.activities.count()
        crop_efficiency.append({
            'name': crop.crop_name,
            'yield': round(float(yield_per_dunum), 2),
            'activities': activity_count
        })

    crop_efficiency_json = json.dumps(crop_efficiency, cls=DjangoJSONEncoder)

    
    agronomist_id = request.session.get('agronomist_id')
    is_managed = False
    if role == 'agronomist' and agronomist_id:
        is_managed = farm.agronomists.filter(id=agronomist_id).exists()


    context = {
        'farm': farm,
        'analysis': analysis,
        'evaluations': evaluations,
        'activities': activities,
        'role': role,
        'crops': crop_data,
        'total_crop_area': total_crop_area,
        'area_exceeded': total_crop_area > farm.total_area,
        'crop_labels': crop_labels,
        'crop_areas': crop_areas,
        'latest_activities': latest_activities,
        'latest_eval': latest_eval,
        'latest_reports': latest_reports,
        'crop_efficiency_json': crop_efficiency_json,
        'agronomist_id': agronomist_id, 
        'is_managed': is_managed,

    }
    return render(request, 'farmDetail.html', context)

def add_crop_to_farm(request, farm_id):
    
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')

    role = request.session.get('role', 'guest')

    # Allowed Roles
    if not (role in ['agronomist', 'user', 'farmer'] or request.user.is_superuser):
        messages.error(request, "Unauthorized access.")
        return redirect('rootsPlusApp:dashboard')

    farm = get_object_or_404(Farm, id=farm_id)

    if request.method == 'POST':
        crop_names = request.POST.getlist('crop_name[]')
        crop_areas = request.POST.getlist('crop_area[]')
        planting_dates = request.POST.getlist('planting_date[]')
        yields = request.POST.getlist('yield_per_dunum[]')
        statuses = request.POST.getlist('status[]')

        total_crop_area = 0
        crops = []

        for i in range(len(crop_names)):
            name = crop_names[i].strip()
            area = crop_areas[i].strip()
            planting_date = planting_dates[i].strip() if i < len(planting_dates) else None
            yield_value = yields[i].strip() if i < len(yields) else None
            status = statuses[i].strip() if i < len(statuses) else None

            if name and area:
                try:
                    area_float = float(area)
                except ValueError:
                    messages.error(request, f"Invalid area value for crop '{name}'.")
                    return render(request, 'addCrops.html', {'farm': farm})

                try:
                    yield_float = float(yield_value) if yield_value else None
                except ValueError:
                    messages.error(request, f"Invalid yield value for crop '{name}'.")
                    return render(request, 'addCrops.html', {'farm': farm})

                total_crop_area += area_float

                crop = Crop(
                    farm=farm,
                    crop_name=name,
                    crop_area=area_float,
                    planting_date=planting_date or None,
                    yield_per_dunum=yield_float,
                    status=status or None
                )
                crops.append(crop)

        farm_area = float(farm.total_area)
        if total_crop_area > farm_area:
            messages.error(request, f"Total crop area ({total_crop_area} dunum) exceeds farm capacity ({farm_area} dunum).")
            return render(request, 'addCrops.html', {'farm': farm})

        for crop in crops:
            crop.save()

        messages.success(request, "Crops added successfully.")
        return redirect('rootsPlusApp:farm_detail', farm_id=farm.id)

    return render(request, 'addCrops.html', {'farm': farm})

def edit_farm_crops(request, farm_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    farm = get_object_or_404(Farm, id=farm_id)
    crops = farm.crops.all()

    if request.method == 'POST':
        crop_ids = request.POST.getlist('crop_id[]')
        crop_names = request.POST.getlist('crop_name[]')
        crop_areas = request.POST.getlist('crop_area[]')
        planting_dates = request.POST.getlist('planting_date[]')
        yields = request.POST.getlist('yield_per_dunum[]')
        statuses = request.POST.getlist('status[]')

        total_crop_area = 0

        for i in range(len(crop_names)):
            crop_id = crop_ids[i].strip() if i < len(crop_ids) else None
            name = crop_names[i].strip()
            area = crop_areas[i].strip()
            planting_date = planting_dates[i].strip() if i < len(planting_dates) else None
            yield_value = yields[i].strip() if i < len(yields) else None
            status = statuses[i].strip() if i < len(statuses) else None

            if not name or not area:
                continue  # Skip Empty Rows

            try:
                area_float = float(area)
            except ValueError:
                messages.error(request, f"Invalid area value for crop '{name}'.")
                return render(request, 'editCrops.html', {'farm': farm, 'crops': crops})

            yield_float = None
            if yield_value:
                try:
                    yield_float = float(yield_value)
                except ValueError:
                    messages.error(request, f"Invalid yield value for crop '{name}'.")
                    return render(request, 'editCrops.html', {'farm': farm, 'crops': crops})

            
            if crop_id:  
                crop = Crop.objects.get(id=crop_id, farm=farm)
            else:        
                crop = Crop(farm=farm)

            crop.crop_name = name
            crop.crop_area = area_float
            crop.planting_date = planting_date or None
            crop.yield_per_dunum = yield_float
            crop.status = status or None
            crop.save()

            total_crop_area += area_float

        if total_crop_area > float(farm.total_area):
            messages.error(request, f"Total crop area ({total_crop_area}) exceeds farm capacity ({farm.total_area}).")
        else:
            messages.success(request, "Crops updated successfully.")
            return redirect('rootsPlusApp:farm_detail', farm_id=farm.id)

    return render(request, 'editCrops.html', {'farm': farm, 'crops': crops})

def delete_farm(request, farm_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    farm = get_object_or_404(Farm, id=farm_id)
    if request.method == "POST":
        farm.delete()
        messages.success(request, "Farm deleted successfully.")
        return redirect('rootsPlusApp:dashboard')  
    return redirect('rootsPlusApp:farmDetail', farm_id=farm.id)

# ---- Farms Management ----
def manage_farm(request, farm_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')

    if request.method != 'POST' or (role != 'agronomist' and not request.user.is_superuser):
        messages.error(request, "Unauthorized access.")
        return redirect('rootsPlusApp:dashboard')

    agronomist_id = request.session.get('agronomist_id')
    agronomist = get_object_or_404(Agronomist, id=agronomist_id)
    farm = get_object_or_404(Farm, id=farm_id)

    farm.agronomists.add(agronomist)
    messages.success(request, f"You are now managing farm: {farm.name}")
    return redirect('rootsPlusApp:farm_detail', farm_id=farm.id)

def unmanage_farm(request, farm_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')
    if role != 'agronomist' and not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('rootsPlusApp:dashboard')

    agro_id = request.session.get('agronomist_id')
    agro = get_object_or_404(Agronomist, id=agro_id)
    farm = get_object_or_404(Farm, id=farm_id)

    if request.method == "POST":
        farm.agronomists.remove(agro)
        messages.success(request, f"You are no longer managing {farm.name}.")
        return redirect('rootsPlusApp:dashboard')

    return redirect('rootsPlusApp:farm_detail', farm_id=farm.id)


# ----- Activities -----
def add_activity(request, farm_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')

    
    if role != 'agronomist' and not request.user.is_superuser:
        messages.error(request, "You are not authorized to add activities.")
        return redirect('rootsPlusApp:dashboard')

    
    if request.user.is_superuser:
        agro = Agronomist.objects.first()  
    else:
        agro_id = request.session.get('agronomist_id')
        agro = get_object_or_404(Agronomist, id=agro_id)

    
    if request.user.is_superuser:
        farm = get_object_or_404(Farm, id=farm_id)
    else:
        farm = get_object_or_404(Farm, id=farm_id, agronomists=agro)

    if request.method == 'POST':
        crop_id = request.POST.get('crop_id')
        crop = get_object_or_404(Crop, id=crop_id, farm=farm)

        Activity.objects.create(
            agronomist=agro,
            farm=farm,
            crop=crop,
            activity_type=request.POST.get('activity_type'),
            date=request.POST.get('date'),
            notes=request.POST.get('notes')
        )

        messages.success(request, "Activity added successfully.")
        return redirect('rootsPlusApp:farm_detail', farm_id=farm.id)

    crops = farm.crops.all()
    activity_types = Activity.ACTIVITY_TYPES
    
    return render(request, 'addActivity.html', {
        'farm': farm,
        'crops': crops,
        'activity_types': activity_types
    })

def farm_activities(request, farm_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')
    user_id = request.session.get(f'{role}_id')
    
    
    if request.user.is_superuser:
        farm = get_object_or_404(Farm, id=farm_id)
    elif role == 'agronomist':
        farm = get_object_or_404(Farm, id=farm_id, agronomists__id=user_id)
    elif role in ['farmer', 'user']:
        farm = get_object_or_404(Farm, id=farm_id, user_id=user_id)
    else:
        messages.error(request, "Unauthorized access.")
        return redirect('rootsPlusApp:dashboard')

    activities = farm.activities.select_related('crop', 'agronomist').order_by('-date')

    return render(request, 'farmActivities.html', {
        'farm': farm,
        'activities': activities,
        'role': role
    })


# ----- Evaluations -----
def add_evaluation(request, farm_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')
    if role != 'agronomist' and not request.user.is_superuser:
        messages.error(request, "You are not authorized to add evaluations.")
        return redirect('rootsPlusApp:dashboard')

    
    if request.user.is_superuser:
        agro = Agronomist.objects.first()  
    else:
        agro_id = request.session.get('agronomist_id')
        agro = get_object_or_404(Agronomist, id=agro_id)

    farm = get_object_or_404(Farm, id=farm_id, agronomists=agro)

    if request.method == 'POST':
        evaluation = Evaluation(
            farm=farm,
            agronomist=agro,
            season=request.POST.get('season'),
            yield_amount=request.POST.get('yield_amount') or None,
            crops_count=request.POST.get('crops_count') or None,
            average_yield_per_dunum=request.POST.get('average_yield_per_dunum') or None,
            activity_score=request.POST.get('activity_score') or None,
            cost_efficiency=request.POST.get('cost_efficiency') or None,
            total_cost=request.POST.get('total_cost') or None,
            recommendations=request.POST.get('recommendations'),
            overall_score=request.POST.get('overall_score') or None
        )
        evaluation.save()
        messages.success(request, "Evaluation added successfully.")
        return redirect('rootsPlusApp:evaluations_list', farm_id=farm.id)

    context = {
        'farm': farm,
        'yield_amount': farm.get_total_farm_yield(),
        'crops_count': farm.get_crops_count(),
        'average_yield_per_dunum': farm.get_average_yield_per_dunum()
    }
    return render(request, 'addEvaluation.html', context)

def evaluation_detail(request, evaluation_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)

    
    if role == 'farmer' and evaluation.farm.user_id != request.session.get('farmer_id'):
        messages.error(request, "You are not authorized to view this evaluation.")
        return redirect('rootsPlusApp:dashboard')

    return render(request, 'evaluationDetail.html', {
        'evaluation': evaluation,
        'role': role
    })

def edit_evaluation(request, evaluation_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')
    if role != 'agronomist' and not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('rootsPlusApp:dashboard')


    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    if request.method == 'POST':
        evaluation.season = request.POST.get('season')
        evaluation.yield_amount = request.POST.get('yield_amount') or None
        evaluation.crops_count = request.POST.get('crops_count') or None
        evaluation.average_yield_per_dunum = request.POST.get('average_yield_per_dunum') or None
        evaluation.activity_score = request.POST.get('activity_score') or None
        evaluation.cost_efficiency = request.POST.get('cost_efficiency') or None
        evaluation.total_cost = request.POST.get('total_cost') or None
        evaluation.recommendations = request.POST.get('recommendations')
        evaluation.overall_score = request.POST.get('overall_score') or None
        evaluation.save()
        messages.success(request, "Evaluation updated successfully.")
        return redirect('rootsPlusApp:evaluation_detail', evaluation_id=evaluation.id)

    return render(request, 'editEvaluation.html', {
        'evaluation': evaluation,
        'farm': evaluation.farm
    })

def delete_evaluation(request, evaluation_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')
    if role != 'agronomist' and not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('rootsPlusApp:dashboard')

    evaluation = get_object_or_404(Evaluation, id=evaluation_id)
    farm_id = evaluation.farm.id
    evaluation.delete()
    messages.success(request, "Evaluation deleted successfully.")
    return redirect('rootsPlusApp:evaluations_list', farm_id=farm_id)

def evaluations_list(request, farm_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')
    user_id = request.session.get(f'{role}_id')
    farm = get_object_or_404(Farm, id=farm_id)

    if request.user.is_superuser:
        evaluations = Evaluation.objects.filter(farm=farm)
    elif role in ['farmer', 'user']:
        farms = Farm.objects.filter(id=farm_id, user_id=user_id)
        evaluations = Evaluation.objects.filter(farm__in=farms)
    elif role == 'agronomist':
        agro = get_object_or_404(Agronomist, id=user_id)
        farms = agro.managed_farms.filter(id=farm_id)
        evaluations = Evaluation.objects.filter(farm__in=farms)
    else:
        evaluations = Evaluation.objects.none()

    return render(request, 'evaluationsList.html', {
        'role': role,
        'evaluations': evaluations,
        'farm': farm,
    })


# ----- Reports -----
def add_report(request, farm_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')
    if role != 'agronomist' and not request.user.is_superuser:
        messages.error(request, "You are not authorized to add reports.")
        return redirect('rootsPlusApp:dashboard')

    if request.user.is_superuser:
        agro = Agronomist.objects.first()
    else:
        agro_id = request.session.get('agronomist_id')
        agro = get_object_or_404(Agronomist, id=agro_id)

    farm = get_object_or_404(Farm, id=farm_id, agronomists=agro)

    if request.method == 'POST':
        season = request.POST.get('season')
        recommendations = request.POST.get('recommendations')
        overall_score = request.POST.get('overall_score')
        notes = request.POST.get('notes')
        status = request.POST.get('status')

        supervisors = ", ".join([a.name for a in farm.agronomists.all()])
        summary = (
            f"Farm: {farm.name}\n"
            f"Location: {farm.location}\n"
            f"Area: {farm.total_area} dunums\n"
            f"Crops Count: {farm.get_crops_count()}\n"
            f"Supervising Agronomists: {supervisors or 'N/A'}\n"
        )

        report = FarmReport(
            farm=farm,
            season=season,
            summary=summary,
            recommendations=recommendations,
            overall_score=overall_score if overall_score else None,
            notes=notes,
            status=status,
            author=agro
        )
        report.save()
        messages.success(request, "Report added successfully.")
        return redirect('rootsPlusApp:reports_list', farm_id=farm.id)

    return render(request, 'addReport.html', {'farm': farm})

def edit_report(request, farm_id, report_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')
    if role != 'agronomist' and not request.user.is_superuser:
        messages.error(request, "You are not authorized to edit reports.")
        return redirect('rootsPlusApp:reports_list', farm_id=farm_id)

    if request.user.is_superuser:
        agro = Agronomist.objects.first()
    else:
        agro_id = request.session.get('agronomist_id')
        agro = get_object_or_404(Agronomist, id=agro_id)

    farm = get_object_or_404(Farm, id=farm_id, agronomists=agro)
    report = get_object_or_404(FarmReport, id=report_id, farm=farm)

    if request.method == 'POST':
        report.season = request.POST.get('season')
        report.recommendations = request.POST.get('recommendations')
        report.overall_score = request.POST.get('overall_score') or None
        report.notes = request.POST.get('notes')
        report.status = request.POST.get('status')

        supervisors = ", ".join([a.name for a in farm.agronomists.all()])
        report.summary = (
            f"Farm: {farm.name}\n"
            f"Location: {farm.location}\n"
            f"Area: {farm.total_area} dunums\n"
            f"Crops Count: {farm.get_crops_count()}\n"
            f"Supervising Agronomists: {supervisors or 'N/A'}\n"
        )

        report.save()
        messages.success(request, "Report updated successfully.")
        return redirect('rootsPlusApp:report_detail', farm_id=farm.id, report_id=report.id)

    return render(request, 'editReport.html', {
        'farm': farm,
        'report': report
    })

def delete_report(request, farm_id, report_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')

    role = request.session.get('role', 'guest')
    if role != 'agronomist' and not request.user.is_superuser:
        messages.error(request, "Unauthorized access.")
        return redirect('rootsPlusApp:dashboard')

    report = get_object_or_404(FarmReport, id=report_id, farm_id=farm_id)
    report.delete()
    messages.success(request, "Report deleted successfully.")
    return redirect('rootsPlusApp:reports_list', farm_id=farm_id)

def reports_list(request, farm_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')
    user_id = request.session.get(f'{role}_id')
    farm = get_object_or_404(Farm, id=farm_id)

    if request.user.is_superuser:
        reports = FarmReport.objects.filter(farm=farm)
    elif role in ['farmer', 'user']:
        farms = Farm.objects.filter(id=farm_id, user_id=user_id)
        reports = FarmReport.objects.filter(farm__in=farms)
    elif role == 'agronomist':
        agro = get_object_or_404(Agronomist, id=user_id)
        farms = agro.managed_farms.filter(id=farm_id)
        reports = FarmReport.objects.filter(farm__in=farms)
    else:
        reports = FarmReport.objects.none()

    return render(request, 'reportsList.html', {
        'role': role,
        'reports': reports,
        'farm': farm,
    })

def report_detail(request, farm_id, report_id):
    if 'role' not in request.session and not request.user.is_superuser:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    role = request.session.get('role', 'guest')

    if request.user.is_superuser:
        report = get_object_or_404(FarmReport, id=report_id, farm_id=farm_id)
    else:
        report = get_object_or_404(FarmReport, id=report_id, farm_id=farm_id)

    return render(request, 'reportDetail.html', {
        'report': report,
        'role': role
    })

def report_export_csv(request, farm_id, report_id):
    if 'role' not in request.session:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    report = get_object_or_404(FarmReport, id=report_id, farm_id=farm_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{report.id}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Field', 'Value'])
    writer.writerow(['Farm', report.farm.name])
    writer.writerow(['Location', report.farm.location])
    writer.writerow(['Season', report.season])
    writer.writerow(['Generated At', report.generated_at])
    writer.writerow(['Overall Score', report.overall_score])
    writer.writerow(['Status', report.status])
    writer.writerow(['Author', report.author.name if report.author else "N/A"])
    writer.writerow(['Summary', report.summary])
    writer.writerow(['Recommendations', report.recommendations])
    writer.writerow(['Notes', report.notes])

    return response


# ----- Profiles -----
def user_profile(request, user_id):
    if 'role' not in request.session:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    profile_user = get_object_or_404(User, id=user_id)

    
    role = request.session.get("role")
    if role not in ["user", "agronomist"]:
        return HttpResponseForbidden("Not allowed")

    farms = profile_user.farms.all().order_by("name")[:7] 
    farm_ids = list(farms.values_list("id", flat=True))
    latest_reports = FarmReport.objects.filter(farm_id__in=farm_ids).order_by("-generated_at")[:5]

    context = {
        "profile_type": "user",
        "profile": profile_user,
        "farms": farms,
        "latest_reports": latest_reports,
    }
    return render(request, "profile.html", context)

def agronomist_profile(request, agronomist_id):
    if 'role' not in request.session:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('loginRegisterApp:loginAccount', role='user')
    
    profile_agro = get_object_or_404(Agronomist, id=agronomist_id)

    farms = Farm.objects.filter(agronomists=profile_agro).order_by("name")[:12]
    farm_ids = list(farms.values_list("id", flat=True))
    latest_reports = FarmReport.objects.filter(farm_id__in=farm_ids).order_by("-generated_at")[:10]

    activities = Activity.objects.filter(agronomist=profile_agro).order_by("-created_at")[:10]
    evaluation = Evaluation.objects.filter(agronomist=profile_agro).order_by("-created_at")[:10]

    context = {
        "profile_type": "agronomist",
        "profile": profile_agro,
        "farms": farms,
        "latest_reports": latest_reports,
        "activities": activities,
        "evaluations": evaluation,
    }
    return render(request, "profile.html", context)


# ----- OpenWeather API ----- 
def farms_weather(request):
    
    role = request.session.get('role')
    weather_data = []
    api_key = "539084667e8e6cf5e2ec379c1368c790"

    if not role:
        return JsonResponse({"error": "Role not found in session"}, status=401)

    
    if role == 'user':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({"error": "User not logged in"}, status=401)
        try:
            current_user = User.objects.get(id=user_id)
            farms = current_user.farms.all()
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

    elif role == 'agronomist':
        agro_id = request.session.get('agronomist_id')
        if not agro_id:
            return JsonResponse({"error": "Agronomist not logged in"}, status=401)
        try:
            current_agro = Agronomist.objects.get(id=agro_id)
            farms = Farm.objects.filter(agronomists=current_agro)
        except Agronomist.DoesNotExist:
            return JsonResponse({"error": "Agronomist not found"}, status=404)

    else:
        farms = Farm.objects.none()

    # 👇 جلب الطقس لكل مزرعة
    for farm in farms:
        if farm.location:  # location = اسم مدينة
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={farm.location}&appid={api_key}&units=metric&lang=en"
                response = requests.get(url)
                data = response.json()

                if data.get("cod") != 200:
                    weather_data.append({
                        "farm": farm.name,
                        "location": farm.location,
                        "error": data.get("message", "Invalid city name")
                    })
                    continue
                offset_seconds = data.get("timezone", 0)
                local_time = datetime.utcnow() + timedelta(seconds=offset_seconds)
                formatted_time = local_time.strftime("%I:%M %p")

                weather_data.append({
                    "farm": farm.name,
                    "location": farm.location,
                    "temp": data["main"]["temp"],
                    "desc": data["weather"][0]["description"],
                    "time": formatted_time  # 👈 أضف الوقت المحلي هنا
                })
            except Exception as e:
                weather_data.append({
                    "farm": farm.name,
                    "location": farm.location,
                    "error": str(e)
                })

    response = JsonResponse(weather_data, safe=False)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

def farm_weather_detail(request, farm_id):
    api_key = "539084667e8e6cf5e2ec379c1368c790"

    try:
        farm = Farm.objects.get(id=farm_id)
    except Farm.DoesNotExist:
        return JsonResponse({"error": "Farm not found"}, status=404)

    if not farm.location:
        return JsonResponse({"error": "Farm has no location"}, status=400)

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={farm.location}&appid={api_key}&units=metric&lang=en"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            return JsonResponse({
                "farm": farm.name,
                "location": farm.location,
                "error": data.get("message", "Invalid city name")
            }, status=400)

        # ✅ حساب الوقت المحلي حسب فرق التوقيت
        offset_seconds = data.get("timezone", 0)
        local_time = datetime.utcnow() + timedelta(seconds=offset_seconds)
        formatted_time = local_time.strftime("%I:%M %p")

        weather_data = {
            "farm": farm.name,
            "location": farm.location,
            "temp": round(data["main"]["temp"]),
            "desc": data["weather"][0]["description"].title(),
            "time": formatted_time  # 👈 الوقت المحلي
        }

        response = JsonResponse(weather_data)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response

    except Exception as e:
        return JsonResponse({
            "farm": farm.name,
            "location": farm.location,
            "error": str(e)
        }, status=500)
