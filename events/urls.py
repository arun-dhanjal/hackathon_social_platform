from . import views
from django.urls import path

app_name = 'events'

urlpatterns = [
    path('', views.EventsList.as_view(), name='events_feed'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
    path('event/<slug:slug>/book/', views.book_event, name='book_event'),
    path('myevents/', views.my_events, name='my_events'),
]
