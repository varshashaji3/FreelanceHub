from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from freelancer.views import  delete_todo,proposal_list,add_new_proposal,add_todo, calendar,AddProfileFreelancer, change_profile_image,freelancer_view,account_settings,change_password, single_project_view,update_profile,view_project,client_list,client_detail,todo

def welcome(request):
    return render(request,'welcome.html')
urlpatterns = [
    path('freelancer_view/', freelancer_view,name="freelancer_view"),
    
    path('add_profile_freelancer/<int:uid>/', AddProfileFreelancer,name="add_profile_freelancer"),
    path('account_settings/', account_settings, name='account_settings'),
    path('change_password/<int:uid>', change_password, name='change_password'),
    path('update_profile/<int:uid>', update_profile, name='update_profile'),
    path('change_profile_image/<int:uid>', change_profile_image, name='change_profile_image'),
    
    path('client_list/', client_list, name='client_list'),
    path('client_detail/<int:cid>', client_detail, name='client_detail'),
    
    path('calendar/', calendar, name='calendar'),
    
    path('todo/', todo, name='todo'),
    
    path('add_todo/<int:user_id>', add_todo, name='add_todo'),
    path('delete_todo/<int:todo_id>', delete_todo, name='delete_todo'),
    
    
    path('view_project/', view_project, name='view_project'),
    
    path('single_project_view/<int:pid>', single_project_view, name='single_project_view'),
    path('add_new_proposal/<int:pid>', add_new_proposal, name='add_new_proposal'),
    path('proposal_list/', proposal_list, name='proposal_list'),
    
]
