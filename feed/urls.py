from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.home, name='home'),  # Root URL redirects to marketplace
    path('feed/', views.feed, name='feed'),  # Social feed (placeholder)
]
