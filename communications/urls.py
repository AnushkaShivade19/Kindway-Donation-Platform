from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.create_event, name='create_event'),
    path('<int:event_id>/volunteer/', views.volunteer_for_event, name='volunteer_for_event'),
    path('story/submit/', views.submit_story, name='submit_story'),
]