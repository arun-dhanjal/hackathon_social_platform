from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content", "image")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Post Title"}),
            "content": forms.Textarea(attrs={"class": "form-control", "placeholder": "Write your post here...", "rows": 4}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        }
