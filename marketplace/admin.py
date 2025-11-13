from django.contrib import admin
from .models import SellingPost, BuyingPost, MarketComment, Listing, Bid, Notification


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """Admin interface for auction listings"""
    list_display = ['title', 'seller', 'starting_price', 'current_price', 'ends_at', 'created_at']
    list_filter = ['created_at', 'ends_at']
    search_fields = ['title', 'description', 'seller__username']
    readonly_fields = ['created_at', 'updated_at', 'current_price']
    fieldsets = (
        ('Basic Information', {
            'fields': ('seller', 'title', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('starting_price', 'reserve_price', 'min_increment', 'current_price')
        }),
        ('Timing', {
            'fields': ('ends_at', 'created_at', 'updated_at')
        }),
    )


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    """Admin interface for bids"""
    list_display = ['listing', 'bidder', 'amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['listing__title', 'bidder__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(SellingPost)
class SellingPostAdmin(admin.ModelAdmin):
    """Admin interface for selling posts (classifieds)"""
    list_display = ['title', 'seller', 'price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'description', 'seller__username']


@admin.register(BuyingPost)
class BuyingPostAdmin(admin.ModelAdmin):
    """Admin interface for buying posts"""
    list_display = ['title', 'buyer', 'min_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'description', 'buyer__username']


@admin.register(MarketComment)
class MarketCommentAdmin(admin.ModelAdmin):
    """Admin interface for marketplace comments"""
    list_display = ['post', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'post__title']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for notifications"""
    list_display = ['recipient', 'sender', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'sender__username', 'message']
    readonly_fields = ['created_at']

