# users/urls.py (new file)

from django.urls import path
from . import views

# Note: Login and Logout are handled by allauth's URLs,
# which we included in the main kindway/urls.py
# We just need to link to them in our templates.

urlpatterns = [
    path('register/donor/', views.donor_register, name='register_donor'),
    path('register/ngo/', views.ngo_register, name='register_ngo'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.search_ngo, name='search_ngo'),
    path('profile/edit/', views.edit_ngo_profile, name='edit_ngo_profile'),
    path('profile/donor/edit/', views.edit_donor_profile, name='edit_donor_profile'),
    path('choose-role/', views.choose_user_role, name='choose_user_role'),

]