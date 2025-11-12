from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path("", views.Feed.as_view(), name="feed"),
    path("post/<int:id>/", views.post_detail, name="post_detail"),
]
