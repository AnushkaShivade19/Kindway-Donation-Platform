from django.urls import path
from . import views

urlpatterns = [
    # --- Primary Donor Flow ---
    # 1. /donations/offer/
    # The main page for a donor to start a donation offer.
    path('offer/', views.offer_donation_flow, name='offer_donation_flow'),

    # 2. /donations/offer/send/<ngo_id>/
    # The endpoint that receives the POST request when a donor chooses an NGO.
    path('offer/send/<int:ngo_id>/', views.send_offer_to_ngo, name='send_offer_to_ngo'),

    # --- Donor-Facing Pages ---
    # 3. /donations/history/
    # Shows the logged-in donor a list of all offers they have sent.
    path('history/', views.offer_history, name='offer_history'),

    # 4. /donations/offer/<offer_id>/
    # The detail page for a single donation offer. (Renamed from donation_detail)
    path('offer/<int:offer_id>/', views.offer_detail, name='offer_detail'),

    # --- NGO-Facing Pages ---
    # 5. /donations/ngo/offers/
    # The inbox for an NGO to see all offers they have received.
    path('ngo/offers/', views.ngo_offer_list, name='ngo_offer_list'),

    # 6. /donations/ngo/request/create/
    # The page for an NGO to post a new "need" (NGORequest).
    path('ngo/request/create/', views.create_ngo_request, name='create_ngo_request'),

    # --- Action Endpoints ---
    # 7. /donations/offer/<offer_id>/update/<new_status>/
    # The endpoint that handles an NGO clicking "accept" or "reject".
    path('offer/<int:offer_id>/update/<str:new_status>/', views.update_offer_status, name='update_offer_status'),

    # 8. /donations/fulfill/<request_id>/
    # The page for a donor to respond to a specific "need" from an NGO.
    path('fulfill/<int:request_id>/', views.fulfill_ngo_request, name='fulfill_ngo_request'),
]