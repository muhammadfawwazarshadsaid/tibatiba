from django.urls import path
from .views import search_oleholeh,getalloleholeh_similarplace,getoleholeh_a_provider,gettopten

app_name = 'oleholeh'
urlpatterns = [
    # path('', getlocation, name='getlocation'),
    path('/gettopten', gettopten, name='gettopten'),
    path('/search_oleholeh/<str:query>', search_oleholeh, name='search_oleholeh'),
    path('/getalloleholeh_similarplace', getalloleholeh_similarplace, name='getalloleholeh_similarplace'),
    path('/getoleholeh_a_provider/<int:provider_id>/', getoleholeh_a_provider, name='getoleholeh_a_provider'),
]
