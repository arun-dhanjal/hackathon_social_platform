from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from cloudinary.models import CloudinaryField
from django.utils import timezone

class Notification(models.Model):
    """Notification system for marketplace transactions"""
    NOTIFICATION_TYPES = (
        ('purchase', 'Purchase Commitment'),
        ('bid', 'New Bid'),
        ('bid_accepted', 'Bid Accepted'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    related_listing = models.ForeignKey('Listing', on_delete=models.CASCADE, null=True, blank=True)
    related_selling_post = models.ForeignKey('SellingPost', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} notification from {self.sender.username} to {self.recipient.username}"

class SellingPost (models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='selling_posts')
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases')
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    image = CloudinaryField('image', default='placeholder')
    
    def __str__(self):
        return self.title

class BuyingPost (models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    image = CloudinaryField('image', default='placeholder')
    
    def __str__(self):
        return self.title

class MarketComment(models.Model):
    post = models.ForeignKey(SellingPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
class Listing(models.Model):
    """Auction-style listing where users can bid"""
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    starting_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reserve_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    min_increment = models.DecimalField(max_digits=12, decimal_places=2, default=1.00)
    ends_at = models.DateTimeField(null=True, blank=True)
    current_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # denormalized for performance
    image = CloudinaryField('image', default='placeholder')
    is_sold = models.BooleanField(default=False)  # Track if item has been sold
    accepted_bid = models.ForeignKey('Bid', on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_for_listing')  # The winning bid
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['ends_at']),
        ]

    def __str__(self):
        return self.title

    def get_highest_bid(self):
        """Get the current highest bid for this listing"""
        return self.bids.order_by('-amount', 'created_at').first()

    def is_auction_ended(self):
        """Check if auction has ended"""
        return self.ends_at and timezone.now() > self.ends_at

    def get_minimum_bid(self):
        """Calculate the minimum valid bid amount"""
        highest = self.get_highest_bid()
        if highest:
            return highest.amount + self.min_increment
        return self.starting_price
    
    def can_accept_bids(self):
        """Check if seller can manually accept bids"""
        return not self.is_sold and self.bids.exists()
    
    def get_winner(self):
        """Get the winning bidder (either accepted bid or highest if auction ended)"""
        if self.accepted_bid:
            return self.accepted_bid
        if self.is_auction_ended():
            return self.get_highest_bid()
        return None


class Bid(models.Model):
    """Bid on an auction listing"""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listing_bids')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-amount', 'created_at']
        indexes = [
            models.Index(fields=['listing', '-amount']),
            models.Index(fields=['bidder', '-created_at']),
        ]

    def __str__(self):
        return f'Bid of £{self.amount} by {self.bidder.username} on {self.listing.title}'

    def clean(self):
        """Validate bid before saving"""
        from django.core.exceptions import ValidationError
        if self.amount <= 0:
            raise ValidationError("Bid amount must be positive.")
        if self.listing.seller_id == self.bidder_id:
            raise ValidationError("You cannot bid on your own listing.")