from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from client.views import  update_proposal_status,freelancer_detail,calendar,AddProfileClient, client_view,account_settings,change_password, project_list, single_project_view,update_profile,change_profile_image,add_new_project,freelancer_list

def welcome(request):
    return render(request,'welcome.html')
urlpatterns = [
    
    path('client_view/', client_view,name="client_view"),
   
    path('add_profile_client/<int:uid>/', AddProfileClient,name="add_profile_client"),
    path('account_settings/', account_settings, name='account_settings'),
    path('change_password/<int:uid>', change_password, name='change_password'),
    
    path('update_profile/<int:uid>', update_profile, name='update_profile'),
    
    path('change_profile_image/<int:uid>', change_profile_image, name='change_profile_image'),
    
    
    path('freelancer_list/', freelancer_list, name='freelancer_list'),
    path('freelancer_detail/<int:fid>', freelancer_detail, name='freelancer_detail'),
    path('calendar/', calendar, name='calendar'),
    
    path('add_new_project/', add_new_project, name='add_new_project'),
    path('project_list/', project_list, name='project_list'),
    path('single_project_view/<int:pid>', single_project_view, name='single_project_view'),
    path('update_proposal_status/<int:pro_id>', update_proposal_status, name='update_proposal_status'),
]
