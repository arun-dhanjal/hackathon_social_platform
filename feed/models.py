from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


# Create your models here.
class Post(models.Model):
    """
    A social media style blog post. Related to :model:`auth.User`.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return f"Post `{self.title}` by {self.author}"


class Comment(models.Model):
    """
    A comment on a post. Related to :model:`feed.Post` and :model:`auth.User`.
    """
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f"Comment on post `{self.post}` by {self.author}"
