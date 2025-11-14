from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from cloudinary.models import CloudinaryField

STATUS = ((0, "Draft"), (1, "Published"))

# Create your models here.


class Event(models.Model):
    """
    Store a single event created by host (user)
    """
    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=200, unique=True, blank=True)
    date = models.DateTimeField()
    location = models.CharField(max_length=150)
    host = models.ForeignKey(
                    User,
                    on_delete=models.CASCADE,
                    related_name="hosted_events")
    description = models.TextField(blank=True)
    featured_image = CloudinaryField('image', default='placeholder')
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    updated_on = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Create slug from title if not already set (from admin)
        # as slug creation is not in host event form
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            # Handle any duplicate titles by using counter
            counter = 1
            while Event.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} | hosted by {self.host}"


class Booking(models.Model):
    """
    Store a event booking related to :model:`events.Event`
    """
    user = models.ForeignKey(
                    User,
                    on_delete=models.CASCADE,
                    related_name="event_booker")
    event = models.ForeignKey(
                    Event,
                    on_delete=models.CASCADE,
                    related_name="event_bookings")
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["booked_at"]

    def __str__(self):
        return f"{self.event} booked by {self.user}"
