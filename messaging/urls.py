from django.urls import path
from . import views

urlpatterns = [
    # This URL will be for your main inbox page
    path('', views.conversation_list, name='conversation_list'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),

]