from django.urls import path
<<<<<<< Updated upstream
from .views import get_users, testvercel
=======
from .views import get_users, logout, register, login
>>>>>>> Stashed changes
app_name = 'mainApp'
urlpatterns = [
    path('users/', get_users, name='get_users'),
<<<<<<< Updated upstream
=======
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    
>>>>>>> Stashed changes
]
