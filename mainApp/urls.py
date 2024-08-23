from django.urls import path
from .views import get_users
app_name = 'mainApp'
urlpatterns = [
    path('users/', get_users, name='get_users'),
]
