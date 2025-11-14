from django.db.models import Q
from feed.models import Post
from events.models import Event
from marketplace.models import SellingPost, BuyingPost, Listing


def search_all(query):
    """
    Search across all content types for a given query string.
    Returns a dictionary with results grouped by type.
    """
    if not query:
        return {
            'posts': [],
            'events': [],
            'selling_posts': [],
            'buying_posts': [],
            'listings': [],
            'total_count': 0
        }
    
    # Search in Feed Posts (title and content)
    posts = Post.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query),
        accepted=True
    ).select_related('author').order_by('-created_on')
    
    # Search in Events (title, description, location)
    events = Event.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query) | 
        Q(location__icontains=query),
        status=1  # Only published events
    ).select_related('host').order_by('-date')
    
    # Search in Selling Posts (title and description)
    selling_posts = SellingPost.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ).select_related('seller').order_by('-created_at')
    
    # Search in Buying Posts (title and description)
    buying_posts = BuyingPost.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ).select_related('buyer').order_by('-created_at')
    
    # Search in Auction Listings (title and description)
    listings = Listing.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ).select_related('seller').order_by('-created_at')
    
    total_count = (
        posts.count() + 
        events.count() + 
        selling_posts.count() + 
        buying_posts.count() + 
        listings.count()
    )
    
    return {
        'posts': posts,
        'events': events,
        'selling_posts': selling_posts,
        'buying_posts': buying_posts,
        'listings': listings,
        'total_count': total_count,
        'query': query
    }
