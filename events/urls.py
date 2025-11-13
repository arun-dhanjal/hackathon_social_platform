from . import views
from django.urls import path

app_name = 'events'

urlpatterns = [
    path('', views.EventsList.as_view(), name='events_feed'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
    path('event/<slug:slug>/book/', views.book_event, name='book_event'),
    path('event/<slug:slug>/cancel/<int:booking_id>/',
         views.cancel_event, name='cancel_event'),
    path('event/<slug:slug>/edit/', views.edit_event, name='edit_event'),
    path('event/<slug:slug>/delete/', views.delete_event, name='delete_event'),
    path('myevents/', views.my_events, name='my_events'),
]
