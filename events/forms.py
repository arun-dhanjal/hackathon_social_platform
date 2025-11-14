from django import forms
from events.models import Event
from django.core.exceptions import ValidationError

# Max upload size (bytes) -- 2MB
MAX_IMAGE_UPLOAD_SIZE = 2 * 1024 * 1024


class HostEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'date', 'location', 'description', 'featured_image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'cols': 4}),
            'featured_image': forms.ClearableFileInput(
                attrs={'class': 'form-control'}
            ),
        }

    def clean_featured_image(self):
        """Validate uploaded image size before sending to Cloudinary.

        If the image is larger than MAX_IMAGE_UPLOAD_SIZE we raise a
        ValidationError with a friendly message. This prevents Cloudinary
        rejecting the upload due to file size and gives the user a clear
        instruction to reduce image dimensions or quality.
        """
        image = self.cleaned_data.get("featured_image")
        if image:
            # Some uploaded files might not have size attribute, guard for that
            size = getattr(image, "size", None)
            if size and size > MAX_IMAGE_UPLOAD_SIZE:
                raise ValidationError(
                    (
                        f"Image file too large ({size // 1024}KB). "
                        f"Please upload an image smaller than "
                        f"{MAX_IMAGE_UPLOAD_SIZE // 1024}KB."
                    )
                )
        return image
