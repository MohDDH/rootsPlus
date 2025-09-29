from django.urls import path
from . import views

app_name = 'rootsPlusApp'

urlpatterns = [
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Farms
    path('farms/add/', views.add_farm, name='add_farm'),
    path('farm/<int:farm_id>/', views.farm_detail, name='farm_detail'),
    path('farm/<int:farm_id>/add-crops/', views.add_crop_to_farm, name='add_crop_to_farm'),
    path('farm/<int:farm_id>/edit-crops/', views.edit_farm_crops, name='edit_farm_crops'),
    path('farm/<int:farm_id>/delete/', views.delete_farm, name='delete_farm'),

    #  Frams Managment
    path('farm/<int:farm_id>/manage/', views.manage_farm, name='manage_farm'),
    path('farm/<int:farm_id>/unmanage/', views.unmanage_farm, name='unmanage_farm'),

    # Activities
    path('farm/<int:farm_id>/activities/add/', views.add_activity, name='add_activity'),
    path('farm/<int:farm_id>/activities/', views.farm_activities, name='farm_activities'),

    # Evaluations
    path('farm/<int:farm_id>/evaluations/', views.evaluations_list, name='evaluations_list'),
    path('farm/<int:farm_id>/evaluations/add/', views.add_evaluation, name='add_evaluation'),
    path('evaluation/<int:evaluation_id>/', views.evaluation_detail, name='evaluation_detail'),
    path('evaluation/<int:evaluation_id>/edit/', views.edit_evaluation, name='edit_evaluation'),
    path('evaluation/<int:evaluation_id>/delete/', views.delete_evaluation, name='delete_evaluation'),

    # Reports
    path('farm/<int:farm_id>/reports/', views.reports_list, name='reports_list'),
    path('farm/<int:farm_id>/reports/add/', views.add_report, name='add_report'),
    path('farm/<int:farm_id>/reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('farm/<int:farm_id>/reports/<int:report_id>/export/csv/', views.report_export_csv, name='report_export_csv'),
    path('farm/<int:farm_id>/report/<int:report_id>/edit/', views.edit_report, name='edit_report'),
    path('farm/<int:farm_id>/report/<int:report_id>/delete/', views.delete_report, name='delete_report'),

    # Profiles
    path("profile/user/<int:user_id>/", views.user_profile, name="user_profile"),
    path("profile/agronomist/<int:agronomist_id>/", views.agronomist_profile, name="agronomist_profile"),

    # OpenWeather API
    path("farms_weather/", views.farms_weather, name="farms_weather"),
    path("farm_weather/<int:farm_id>/", views.farm_weather_detail, name="farm_weather_detail"),

    

]



