
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from administrator.views import admin_view,user_list,toggle_status,toggle_permission,change_profile_image,account_settings,change_password


urlpatterns = [
    
   path('admin_view/', admin_view,name="admin_view"),
   path('user_list/',user_list,name="user_list"),
   path('toggle_status/<int:uid>',toggle_status,name="toggle_status"),
   
   path('toggle_permission/<int:uid>',toggle_permission,name="toggle_permission"),
   path('change_profile_image/<int:uid>', change_profile_image, name='change_profile_image'),
   path('account_settings/', account_settings, name='account_settings'),
   path('change_password/<int:uid>', change_password, name='change_password'),
]


