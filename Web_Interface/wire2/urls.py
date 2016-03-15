"""wire2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import patterns, include, url
from django.contrib import admin

#from sound_engine import views

urlpatterns = [
    url(r'^$','sound_engine.views.home', name='home'),
    url(r'^$','sound_engine.views.SearchResults', name='SearchResults'),
    url(r'^$','../static/temp_wet.wav', name = 'wet_wav'),
    url(r'^$','../static/temp_dry.wav', name = 'dry_wav'),
    url(r'^$','../static/temp_wet.png', name = 'wet_png'),
    url(r'^$','../static/temp_dry.png', name = 'dry_png'),
]

