"""fuzzyaitest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import index, createGame, register, completed, rules
from game.views import game
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', index, name='homepage'),
    path('game/<int:game_id>', game, name = 'game'),
    path('create/', createGame.as_view(), name = 'create'),
    path('register/', register.as_view(), name = 'register'),
    path('completed/', completed, name = 'completed'),
    path('rules/', rules, name = 'rules'),
]
urlpatterns += staticfiles_urlpatterns()
