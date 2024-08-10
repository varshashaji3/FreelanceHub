
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from core.views import   about, add_user_type, contact, email_verification, index, login, login_view, logout, register, register_view, reset_password, send_forget_password_mail, send_verification_mail, service,faqs


urlpatterns = [
    path('',index,name="index"),
    path('about/',about,name="about"),
    path('contact/',contact,name="contact"),
    path('login/',login,name="login"),
    path('service/',service,name="service"),
    path('faqs/',faqs,name="faqs"),
    path('register_view/', register_view,name="register_view"),
    path('login_view/', login_view,name="login_view"),
    
    path('add_user_type/<int:uid>', add_user_type,name="add_user_type"),
    path('register/', register,name="register"),
    path('logout/', logout,name="logout"),
    
    
    path('send_forget_password_mail/', send_forget_password_mail,name="send_forget_password_mail"),
    path('reset_password/<token>/', reset_password,name="reset_password"),
    path('send_verification_mail/', send_verification_mail, name="send_verification_mail"),
    path('email_verification/<token>/', email_verification, name="email_verification"),

    
  
]
