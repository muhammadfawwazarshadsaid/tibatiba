from django.urls import path
from .views import search_posts
app_name = 'mainApp'
urlpatterns = [
    path('search_posts/', search_posts, name='search_posts'),
]
