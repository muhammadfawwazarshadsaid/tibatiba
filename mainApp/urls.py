from django.urls import path
from .views import get_users, testvercel
app_name = 'mainApp'
urlpatterns = [
    path('', testvercel, name='testvercel'),
    path('users/', get_users, name='get_users'),
    #  path('register/', RegisterUserView.as_view(), name='register'),
]
