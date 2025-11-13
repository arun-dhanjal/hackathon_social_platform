from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Main marketplace feed
    path('', views.marketplace_feed, name='marketplace_feed'),
    
    # Selling posts (classifieds)
    path('selling/create/', views.create_selling_post, name='create_selling_post'),
    path('selling/<int:pk>/', views.selling_post_detail, name='selling_post_detail'),
    path('selling/<int:pk>/commit-buy/', views.commit_to_buy, name='commit_to_buy'),
    
    # Buying posts (wanted ads)
    path('buying/create/', views.create_buying_post, name='create_buying_post'),
    
    # Auction listings
    path('listing/create/', views.create_listing, name='create_listing'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('listing/<int:pk>/bid/', views.place_bid, name='place_bid'),
    path('listing/<int:pk>/delete/', views.delete_listing, name='delete_listing'),
    path('listing/<int:listing_pk>/accept-bid/<int:bid_pk>/', views.accept_bid, name='accept_bid'),
    
    # User views
    path('my-bids/', views.my_bids, name='my_bids'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
]
