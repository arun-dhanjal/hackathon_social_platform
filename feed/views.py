from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic
from .models import Post, Comment


# Create your views here.
class Feed(generic.ListView):
    template_name = "feed/feed.html"
    context_object_name = "posts"
    paginate_by = 6

    queryset = Post.objects.all().filter(accepted=True).order_by("-created_on")


def post_detail(request, id):
    queryset = Post.objects.filter(accepted=True)
    post = get_object_or_404(queryset, id=id)

    comments = post.comments.all().order_by("-created_on")
    comment_count = post.comments.filter(accepted=True).count()

    return render(
        request,
        "feed/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_count": comment_count,
        }
    )
