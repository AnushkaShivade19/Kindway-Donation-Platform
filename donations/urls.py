from django.urls import path
from . import views

urlpatterns = [
    path('<int:donation_id>/request/', views.request_donation, name='request_donation'),
    path('<int:donation_id>/', views.donation_detail, name='donation_detail'),
    
    # --- URLs for the new direct donation flow ---
    path('offer/', views.offer_donation_flow, name='offer_donation_flow'),
    path('offer/send/<int:ngo_id>/', views.send_offer_to_ngo, name='send_offer_to_ngo'),
    path('offer/', views.offer_donation_flow, name='offer_donation_flow'),
    path('offer/send/<int:ngo_id>/', views.send_offer_to_ngo, name='send_offer_to_ngo'),
    path('ngo/request/create/', views.create_ngo_request, name='create_ngo_request'),

    # --- New URL for the offer history page ---
    path('history/', views.offer_history, name='offer_history'),
    path('ngo/offers/', views.ngo_offer_list, name='ngo_offer_list'),
    path('offer/<int:offer_id>/update/<str:new_status>/', views.update_offer_status, name='update_offer_status'),
    path('fulfill/<int:request_id>/', views.fulfill_ngo_request, name='fulfill_ngo_request'),
]
