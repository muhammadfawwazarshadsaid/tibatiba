from django.urls import path
from .views import getall, getlocation

app_name = 'oleholeh'
urlpatterns = [
    path('', getlocation, name='getlocation'),
]
