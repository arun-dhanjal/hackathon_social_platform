from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.contrib import messages
from django.http import HttpResponseForbidden
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
    try:
        post = Post.objects.get(id=id)
        if not post.accepted and post.author != request.user:
            raise Post.DoesNotExist
    except Post.DoesNotExist:
        return render(request, "404.html", status=404)

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


@login_required
def edit_post(request, id):
    """
    Allows post authors to edit their :model:`feed.Post`.

    Resets approval status and optionally removes the image.

    **Context**

    ``form``
        An instance of :form:`feed.PostForm`.
    ``post``
        The :model:`feed.Post` being edited.

    **Template**

    :template:`feed/edit_post.html`
    """
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:
        return HttpResponseForbidden("You can't edit this post.")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.is_approved = False
            post.save()
            messages.success(
                request,
                "Post edited successfully - status "
                "changed to 'Pending approval'."
            )
            return redirect("feed:post_detail", id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "feed/edit_post.html", {
        "form": form,
        "post": post,
    })


@login_required
def delete_post(request, id):
    """
    Allows post authors to delete their :model:`feed.Post`.

    Redirects to the feed after deletion.
    """
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:
        return HttpResponseForbidden("You can't delete this post.")

    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect("feed:feed")