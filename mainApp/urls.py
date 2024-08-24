from django.urls import path
from .views import get_users, search_posts, testvercel
app_name = 'mainApp'
urlpatterns = [
    path('', testvercel, name='testvercel'),
    path('users/', get_users, name='get_users'),
    path('search_posts/', search_posts, name='search_posts'),
]
