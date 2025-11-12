from django.shortcuts import render
from django.views import generic
from .models import Post, Comment


# Create your views here.
class Feed(generic.ListView):
    template_name = "feed/feed.html"
    context_object_name = "posts"
    paginate_by = 6

    queryset = Post.objects.all().filter(accepted=True).order_by("-created_on")
