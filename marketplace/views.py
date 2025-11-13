from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from .models import SellingPost, BuyingPost, MarketComment, Bid, Listing, Notification


def marketplace_feed(request):
    selling_posts = SellingPost.objects.all().order_by('-created_at')
    buying_posts = BuyingPost.objects.all().order_by('-created_at')
    listings = Listing.objects.all().order_by('-created_at')
    
    # Get user's listings if authenticated
    my_listings = []
    my_selling_posts = []
    my_buying_posts = []
    if request.user.is_authenticated:
        my_listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
        my_selling_posts = SellingPost.objects.filter(seller=request.user).order_by('-created_at')
        my_buying_posts = BuyingPost.objects.filter(buyer=request.user).order_by('-created_at')
    
    context = {
        'selling_posts': selling_posts,
        'buying_posts': buying_posts,
        'listings': listings,
        'my_listings': my_listings,
        'my_selling_posts': my_selling_posts,
        'my_buying_posts': my_buying_posts,
    }
    return render(request, 'marketplace/marketplace_feed.html', context)

@login_required
def create_selling_post(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        price = request.POST['price']
        image = request.FILES.get('image')
        seller = request.user

        SellingPost.objects.create(
            title=title,
            description=description,
            price=price,
            seller=seller,
            image=image
        )
        messages.success(request, 'Selling post created successfully!')
        return redirect('marketplace:marketplace_feed')
    return render(request, 'marketplace/create_selling_post.html')

@login_required
def create_listing(request):
    """Create an auction-style listing"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        starting_price = request.POST.get('starting_price')
        reserve_price = request.POST.get('reserve_price')
        min_increment = request.POST.get('min_increment', '1.00')
        ends_at = request.POST.get('ends_at')
        image = request.FILES.get('image')

        try:
            listing = Listing.objects.create(
                title=title,
                description=description,
                starting_price=Decimal(starting_price),
                reserve_price=Decimal(reserve_price) if reserve_price else None,
                min_increment=Decimal(min_increment),
                ends_at=ends_at if ends_at else None,
                seller=request.user,
                image=image
            )
            messages.success(request, 'Auction listing created successfully!')
            return redirect('marketplace:listing_detail', pk=listing.pk)
        except (ValueError, InvalidOperation) as e:
            messages.error(request, f'Invalid input: {str(e)}')
    
    return render(request, 'marketplace/create_listing.html')

@login_required
def listing_detail(request, pk):
    """Display a single listing with all bids"""
    listing = get_object_or_404(Listing, pk=pk)
    bids = listing.bids.all()[:10]  # Show top 10 bids
    highest_bid = listing.get_highest_bid()
    minimum_bid = listing.get_minimum_bid()
    is_ended = listing.is_auction_ended()
    
    context = {
        'listing': listing,
        'bids': bids,
        'highest_bid': highest_bid,
        'minimum_bid': minimum_bid,
        'is_ended': is_ended,
        'is_seller': request.user == listing.seller,
    }
    return render(request, 'marketplace/listing_detail.html', context)

@login_required
def place_bid(request, pk):
    """Place a bid on a listing with atomic transaction and race condition protection"""
    if request.method != 'POST':
        return redirect('marketplace:listing_detail', pk=pk)

    listing = get_object_or_404(Listing, pk=pk)
    
    # Parse bid amount
    try:
        amount = Decimal(request.POST.get('amount', '0').strip())
    except (ValueError, InvalidOperation):
        messages.error(request, "Invalid bid amount.")
        return redirect('marketplace:listing_detail', pk=pk)

    # Basic validation
    if amount <= 0:
        messages.error(request, "Bid amount must be positive.")
        return redirect('marketplace:listing_detail', pk=pk)

    # Prevent seller from bidding on own listing
    if listing.seller == request.user:
        messages.error(request, "You cannot bid on your own listing.")
        return redirect('marketplace:listing_detail', pk=pk)

    # Use atomic transaction with row-level locking to prevent race conditions
    try:
        with transaction.atomic():
            # Lock the listing row so concurrent bidders serialize here
            listing = Listing.objects.select_for_update().get(pk=listing.pk)
            
            # Check if listing has been sold
            if listing.is_sold:
                messages.error(request, "This listing has already been sold.")
                return redirect('marketplace:listing_detail', pk=pk)
            
            # Check if auction has ended
            if listing.is_auction_ended():
                messages.error(request, "This auction has ended.")
                return redirect('marketplace:listing_detail', pk=pk)

            # Get minimum required bid
            minimum_bid = listing.get_minimum_bid()

            # Validate bid amount
            if amount < minimum_bid:
                messages.error(request, f"Minimum bid is £{minimum_bid}. Your bid of £{amount} is too low.")
                return redirect('marketplace:listing_detail', pk=pk)

            # Create the bid
            bid = Bid.objects.create(
                listing=listing,
                bidder=request.user,
                amount=amount
            )

            # Update denormalized current_price for performance
            listing.current_price = amount
            listing.save(update_fields=['current_price', 'updated_at'])

            messages.success(request, f"Your bid of £{amount} was placed successfully!")
            return redirect('marketplace:listing_detail', pk=pk)

    except Exception as e:
        messages.error(request, f"An error occurred while placing your bid: {str(e)}")
        return redirect('marketplace:listing_detail', pk=pk)

@login_required
def my_bids(request):
    """Show all bids placed by the current user"""
    bids = Bid.objects.filter(bidder=request.user).select_related('listing').order_by('-created_at')
    context = {
        'bids': bids,
    }
    return render(request, 'marketplace/my_bids.html', context)

@login_required
def my_listings(request):
    """Show all listings created by the current user"""
    listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
    context = {
        'listings': listings,
    }
    return render(request, 'marketplace/my_listings.html', context)


def selling_post_detail(request, pk):
    """Display detail page for a selling post"""
    post = get_object_or_404(SellingPost, pk=pk)
    context = {
        'post': post,
    }
    return render(request, 'marketplace/selling_post_detail.html', context)


@login_required
def commit_to_buy(request, pk):
    """Commit to buy a selling post"""
    if request.method != 'POST':
        return redirect('marketplace:selling_post_detail', pk=pk)
    
    post = get_object_or_404(SellingPost, pk=pk)
    
    # Can't buy your own post
    if post.seller == request.user:
        messages.error(request, "You cannot buy your own item.")
        return redirect('marketplace:selling_post_detail', pk=pk)
    
    # Check if already sold
    if post.is_sold:
        messages.error(request, "This item has already been sold.")
        return redirect('marketplace:selling_post_detail', pk=pk)
    
    # Mark as sold and assign buyer
    try:
        with transaction.atomic():
            post.buyer = request.user
            post.is_sold = True
            post.save(update_fields=['buyer', 'is_sold'])
            
            # Create notification for seller
            Notification.objects.create(
                recipient=post.seller,
                sender=request.user,
                notification_type='purchase',
                message=f"{request.user.username} has committed to buy your item '{post.title}' for £{post.price}.",
                related_selling_post=post
            )
        
        messages.success(
            request,
            f"You've committed to buy '{post.title}' for £{post.price}. "
            f"The seller {post.seller.username} has been notified and will contact you."
        )
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    
    return redirect('marketplace:selling_post_detail', pk=pk)


@login_required
def accept_bid(request, listing_pk, bid_pk):
    """Allow seller to accept a specific bid and mark listing as sold"""
    if request.method != 'POST':
        return redirect('marketplace:listing_detail', pk=listing_pk)
    
    listing = get_object_or_404(Listing, pk=listing_pk)
    bid = get_object_or_404(Bid, pk=bid_pk, listing=listing)
    
    # Only the seller can accept bids
    if listing.seller != request.user:
        messages.error(request, "You can only accept bids on your own listings.")
        return redirect('marketplace:listing_detail', pk=listing_pk)
    
    # Check if already sold
    if listing.is_sold:
        messages.error(request, "This listing has already been sold.")
        return redirect('marketplace:listing_detail', pk=listing_pk)
    
    # Accept the bid
    try:
        with transaction.atomic():
            listing.accepted_bid = bid
            listing.is_sold = True
            listing.save(update_fields=['accepted_bid', 'is_sold', 'updated_at'])
        
        messages.success(
            request, 
            f"You've accepted {bid.bidder.username}'s bid of £{bid.amount}. "
            f"Please contact them to complete the transaction."
        )
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    
    return redirect('marketplace:listing_detail', pk=listing_pk)


@login_required
def notifications(request):
    """Display all notifications for the current user"""
    user_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = user_notifications.filter(is_read=False).count()
    
    context = {
        'notifications': user_notifications,
        'unread_count': unread_count,
    }
    return render(request, 'marketplace/notifications.html', context)


@login_required
def mark_notification_read(request, pk):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('marketplace:notifications')


@login_required
def delete_listing(request, pk):
    """Allow seller to delete their listing if no bids have been placed"""
    listing = get_object_or_404(Listing, pk=pk)
    
    # Only the seller can delete the listing
    if listing.seller != request.user:
        messages.error(request, "You can only delete your own listings.")
        return redirect('marketplace:listing_detail', pk=pk)
    
    # Prevent deletion if bids exist
    if listing.bids.exists():
        messages.error(request, "Cannot delete listing with existing bids.")
        return redirect('marketplace:listing_detail', pk=pk)
    
    # Delete the listing
    listing.delete()
    messages.success(request, "Listing deleted successfully.")
    return redirect('marketplace:my_listings')