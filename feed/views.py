from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic
from django.contrib import messages
from django.db import models
from .models import Post, Comment
from .forms import PostForm, CommentForm


# Create your views here.
class Feed(generic.ListView):
    template_name = "feed/feed.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Post.objects.filter(
                (models.Q(accepted=True)) | (models.Q(author=user))
            ).order_by("-created_on").distinct()
        return Post.objects.filter(accepted=True).order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        post_form = PostForm(data=request.POST)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.save()
            messages.add_message(
                request, messages.SUCCESS,
                "Post submitted and awaiting approval."
            )
        return self.get(request, *args, **kwargs)


def post_detail(request, id):
    queryset = Post.objects.filter(accepted=True)
    post = get_object_or_404(queryset, id=id)

    comments = post.comments.all().order_by("created_on")
    comment_count = post.comments.filter(accepted=True).count()
    
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.add_message(
                request, messages.SUCCESS,
                "Comment submitted and awaiting approval."
            )
    
    comment_form = CommentForm()

    return render(
        request,
        "feed/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_count": comment_count,
            "comment_form": comment_form,
        }
    )
