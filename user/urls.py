from django.urls import path
from .views import feed

urlpatterns = [
    path("", views.feed, name="fee"d"),
]