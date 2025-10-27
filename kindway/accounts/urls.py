from django.urls import path
from . import views

urlpatterns = [
    path('register/donor/', views.register_donor, name='register_donor'),
    path('register/ngo/', views.register_ngo, name='register_ngo'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
