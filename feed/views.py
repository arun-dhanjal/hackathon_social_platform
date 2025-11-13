from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic
from django.contrib import messages
from .models import Post, Comment
from .forms import PostForm


# Create your views here.
class Feed(generic.ListView):
    template_name = "feed/feed.html"
    context_object_name = "posts"
    paginate_by = 6
    queryset = Post.objects.filter(accepted=True).order_by("-created_on")

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
                'Post submitted and awaiting approval'
            )
        return self.get(request, *args, **kwargs)


def post_detail(request, id):
    queryset = Post.objects.filter(accepted=True)
    post = get_object_or_404(queryset, id=id)

    comments = post.comments.all().order_by("created_on")
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
