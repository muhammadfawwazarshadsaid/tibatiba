from django.urls import path
from .views import get_users, logout, register, login
app_name = 'mainApp'
urlpatterns = [
    path('users/', get_users, name='get_users'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    
]
