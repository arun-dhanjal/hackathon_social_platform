import unittest
from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db import connection
from decimal import Decimal
from datetime import timedelta
from threading import Thread
from time import sleep
from .models import Listing, Bid, SellingPost, BuyingPost, Notification, MarketComment


class ListingModelTest(TestCase):
    """Test the Listing model"""

    def setUp(self):
        self.user = User.objects.create_user(username='seller', password='testpass123')
        self.listing = Listing.objects.create(
            seller=self.user,
            title='Test Item',
            description='Test description',
            starting_price=Decimal('10.00'),
            min_increment=Decimal('1.00'),
        )

    def test_listing_creation(self):
        """Test that a listing is created correctly"""
        self.assertEqual(self.listing.title, 'Test Item')
        self.assertEqual(self.listing.starting_price, Decimal('10.00'))
        self.assertEqual(self.listing.seller, self.user)

    def test_get_minimum_bid_no_bids(self):
        """Test minimum bid when there are no bids"""
        self.assertEqual(self.listing.get_minimum_bid(), Decimal('10.00'))

    def test_get_minimum_bid_with_bids(self):
        """Test minimum bid calculation with existing bids"""
        bidder = User.objects.create_user(username='bidder', password='testpass123')
        Bid.objects.create(listing=self.listing, bidder=bidder, amount=Decimal('15.00'))

        expected_min = Decimal('15.00') + Decimal('1.00')  # 15 + 1 = 16
        self.assertEqual(self.listing.get_minimum_bid(), expected_min)

    def test_get_highest_bid(self):
        """Test getting the highest bid"""
        bidder1 = User.objects.create_user(username='bidder1', password='testpass123')
        bidder2 = User.objects.create_user(username='bidder2', password='testpass123')

        Bid.objects.create(listing=self.listing, bidder=bidder1, amount=Decimal('15.00'))
        highest_bid = Bid.objects.create(listing=self.listing, bidder=bidder2, amount=Decimal('20.00'))

        self.assertEqual(self.listing.get_highest_bid(), highest_bid)
        self.assertEqual(self.listing.get_highest_bid().amount, Decimal('20.00'))

    def test_is_auction_ended_no_end_date(self):
        """Test auction with no end date is not ended"""
        self.assertFalse(self.listing.is_auction_ended())

    def test_is_auction_ended_future(self):
        """Test auction with future end date is not ended"""
        self.listing.ends_at = timezone.now() + timedelta(days=1)
        self.listing.save()
        self.assertFalse(self.listing.is_auction_ended())

    def test_is_auction_ended_past(self):
        """Test auction with past end date is ended"""
        self.listing.ends_at = timezone.now() - timedelta(days=1)
        self.listing.save()
        self.assertTrue(self.listing.is_auction_ended())


class BidModelTest(TestCase):
    """Test the Bid model"""

    def setUp(self):
        self.seller = User.objects.create_user(username='seller', password='testpass123')
        self.bidder = User.objects.create_user(username='bidder', password='testpass123')
        self.listing = Listing.objects.create(
            seller=self.seller,
            title='Test Item',
            starting_price=Decimal('10.00'),
            min_increment=Decimal('1.00'),
        )

    def test_bid_creation(self):
        """Test that a bid is created correctly"""
        bid = Bid.objects.create(
            listing=self.listing,
            bidder=self.bidder,
            amount=Decimal('15.00')
        )
        self.assertEqual(bid.amount, Decimal('15.00'))
        self.assertEqual(bid.bidder, self.bidder)
        self.assertEqual(bid.listing, self.listing)

    def test_bid_ordering(self):
        """Test that bids are ordered by amount descending"""
        bidder2 = User.objects.create_user(username='bidder2', password='testpass123')

        bid1 = Bid.objects.create(listing=self.listing, bidder=self.bidder, amount=Decimal('15.00'))
        bid2 = Bid.objects.create(listing=self.listing, bidder=bidder2, amount=Decimal('20.00'))

        bids = list(Bid.objects.all())
        self.assertEqual(bids[0], bid2)  # Higher bid first
        self.assertEqual(bids[1], bid1)


class BidPlacementViewTest(TestCase):
    """Test the bid placement view"""

    def setUp(self):
        self.client = Client()
        self.seller = User.objects.create_user(username='seller', password='testpass123')
        self.bidder = User.objects.create_user(username='bidder', password='testpass123')
        self.listing = Listing.objects.create(
            seller=self.seller,
            title='Test Item',
            starting_price=Decimal('10.00'),
            min_increment=Decimal('1.00'),
        )

    def test_place_bid_success(self):
        """Test successfully placing a valid bid"""
        self.client.login(username='bidder', password='testpass123')

        response = self.client.post(
            reverse('marketplace:place_bid', kwargs={'pk': self.listing.pk}),
            {'amount': '15.00'}
        )

        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(Bid.objects.count(), 1)
        bid = Bid.objects.first()
        self.assertEqual(bid.amount, Decimal('15.00'))
        self.assertEqual(bid.bidder, self.bidder)

    def test_place_bid_not_authenticated(self):
        """Test that unauthenticated users cannot place bids"""
        response = self.client.post(
            reverse('marketplace:place_bid', kwargs={'pk': self.listing.pk}),
            {'amount': '15.00'}
        )

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Bid.objects.count(), 0)

    def test_place_bid_seller_cannot_bid(self):
        """Test that sellers cannot bid on their own listings"""
        self.client.login(username='seller', password='testpass123')

        response = self.client.post(
            reverse('marketplace:place_bid', kwargs={'pk': self.listing.pk}),
            {'amount': '15.00'}
        )

        self.assertEqual(Bid.objects.count(), 0)

    def test_place_bid_too_low(self):
        """Test that bids below minimum are rejected"""
        self.client.login(username='bidder', password='testpass123')

        # First bid
        Bid.objects.create(listing=self.listing, bidder=self.bidder, amount=Decimal('15.00'))

        # Try to place a bid that's too low (should be at least 16.00)
        response = self.client.post(
            reverse('marketplace:place_bid', kwargs={'pk': self.listing.pk}),
            {'amount': '15.50'}
        )

        # Should have only 1 bid (the first one)
        self.assertEqual(Bid.objects.count(), 1)

    def test_place_bid_on_ended_auction(self):
        """Test that bids cannot be placed on ended auctions"""
        self.listing.ends_at = timezone.now() - timedelta(days=1)
        self.listing.save()

        self.client.login(username='bidder', password='testpass123')

        response = self.client.post(
            reverse('marketplace:place_bid', kwargs={'pk': self.listing.pk}),
            {'amount': '15.00'}
        )

        self.assertEqual(Bid.objects.count(), 0)

    def test_place_bid_updates_current_price(self):
        """Test that placing a bid updates the listing's current_price"""
        self.client.login(username='bidder', password='testpass123')

        self.client.post(
            reverse('marketplace:place_bid', kwargs={'pk': self.listing.pk}),
            {'amount': '15.00'}
        )

        self.listing.refresh_from_db()
        self.assertEqual(self.listing.current_price, Decimal('15.00'))

    def test_place_bid_invalid_amount(self):
        """Test that invalid bid amounts are rejected"""
        self.client.login(username='bidder', password='testpass123')

        # Negative amount
        response = self.client.post(
            reverse('marketplace:place_bid', kwargs={'pk': self.listing.pk}),
            {'amount': '-5.00'}
        )
        self.assertEqual(Bid.objects.count(), 0)

        # Zero amount
        response = self.client.post(
            reverse('marketplace:place_bid', kwargs={'pk': self.listing.pk}),
            {'amount': '0'}
        )
        self.assertEqual(Bid.objects.count(), 0)

        # Invalid string
        response = self.client.post(
            reverse('marketplace:place_bid', kwargs={'pk': self.listing.pk}),
            {'amount': 'invalid'}
        )
        self.assertEqual(Bid.objects.count(), 0)


class BidConcurrencyTest(TransactionTestCase):
    """Test concurrent bid placement (race conditions)"""

    def setUp(self):
        self.seller = User.objects.create_user(username='seller', password='testpass123')
        self.bidder1 = User.objects.create_user(username='bidder1', password='testpass123')
        self.bidder2 = User.objects.create_user(username='bidder2', password='testpass123')
        self.listing = Listing.objects.create(
            seller=self.seller,
            title='Test Item',
            starting_price=Decimal('10.00'),
            min_increment=Decimal('1.00'),
        )

    @unittest.skipIf(connection.vendor == 'sqlite', 'SQLite does not support concurrent writes reliably')
    def test_concurrent_bids(self):
        """Test that concurrent bids are handled correctly with select_for_update"""
        errors = []

        def place_bid(username, password, amount):
            """Helper function to place a bid in a thread"""
            try:
                client = Client()
                client.login(username=username, password=password)
                client.post(
                    reverse('marketplace:place_bid', kwargs={'pk': self.listing.pk}),
                    {'amount': str(amount)}
                )
            except Exception as e:
                errors.append(str(e))

        # Create threads to simulate concurrent bidding
        thread1 = Thread(target=place_bid, args=('bidder1', 'testpass123', Decimal('15.00')))
        thread2 = Thread(target=place_bid, args=('bidder2', 'testpass123', Decimal('16.00')))

        # Start both threads at roughly the same time
        thread1.start()
        thread2.start()

        # Wait for both to complete
        thread1.join()
        thread2.join()

        # Check that both bids were accepted (since both are valid)
        self.assertEqual(Bid.objects.count(), 2)

        # Check that the highest bid is correct
        highest = self.listing.get_highest_bid()
        self.assertEqual(highest.amount, Decimal('16.00'))

        # No errors should have occurred
        self.assertEqual(len(errors), 0)


class ListingViewsTest(TestCase):
    """Test listing-related views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.listing = Listing.objects.create(
            seller=self.user,
            title='Test Item',
            starting_price=Decimal('10.00'),
        )

    def test_listing_detail_view(self):
        """Test the listing detail view"""
        response = self.client.get(
            reverse('marketplace:listing_detail', kwargs={'pk': self.listing.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
        self.assertContains(response, '£10')  # Template uses £ not $

    def test_my_bids_view_authenticated(self):
        """Test my bids view for authenticated user"""
        bidder = User.objects.create_user(username='bidder', password='testpass123')
        Bid.objects.create(listing=self.listing, bidder=bidder, amount=Decimal('15.00'))

        self.client.login(username='bidder', password='testpass123')
        response = self.client.get(reverse('marketplace:my_bids'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')

    def test_my_listings_view_authenticated(self):
        """Test my listings view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('marketplace:my_listings'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')


# ===== SELLING POST TESTS =====

class SellingPostModelTest(TestCase):
    """Test the SellingPost model"""

    def setUp(self):
        self.seller = User.objects.create_user(username='seller', password='testpass123')
        self.buyer = User.objects.create_user(username='buyer', password='testpass123')

    def test_selling_post_creation(self):
        """Test creating a SellingPost"""
        post = SellingPost.objects.create(
            title='iPhone 13',
            description='Like new condition',
            price=Decimal('500.00'),
            seller=self.seller
        )

        self.assertEqual(post.title, 'iPhone 13')
        self.assertEqual(post.price, Decimal('500.00'))
        self.assertEqual(post.seller, self.seller)
        self.assertFalse(post.is_sold)
        self.assertIsNone(post.buyer)

    def test_selling_post_string_representation(self):
        """Test __str__ method"""
        post = SellingPost.objects.create(
            title='Test Item',
            description='Test',
            price=Decimal('100.00'),
            seller=self.seller
        )
        self.assertEqual(str(post), 'Test Item')

    def test_selling_post_mark_as_sold(self):
        """Test marking a post as sold"""
        post = SellingPost.objects.create(
            title='Test Item',
            description='Test',
            price=Decimal('100.00'),
            seller=self.seller
        )

        post.is_sold = True
        post.buyer = self.buyer
        post.save()

        post.refresh_from_db()
        self.assertTrue(post.is_sold)
        self.assertEqual(post.buyer, self.buyer)


class SellingPostViewTest(TestCase):
    """Test SellingPost CRUD views"""

    def setUp(self):
        self.client = Client()
        self.seller = User.objects.create_user(username='seller', password='testpass123')
        self.buyer = User.objects.create_user(username='buyer', password='testpass123')

    def test_create_selling_post_authenticated(self):
        """Test creating a selling post when logged in"""
        self.client.login(username='seller', password='testpass123')

        response = self.client.post(reverse('marketplace:create_selling_post'), {
            'title': 'Gaming Laptop',
            'description': 'High performance laptop',
            'price': '800.00',
        })

        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(SellingPost.objects.count(), 1)

        post = SellingPost.objects.first()
        self.assertEqual(post.title, 'Gaming Laptop')
        self.assertEqual(post.price, Decimal('800.00'))
        self.assertEqual(post.seller, self.seller)

    def test_create_selling_post_unauthenticated(self):
        """Test that unauthenticated users cannot create posts"""
        response = self.client.post(reverse('marketplace:create_selling_post'), {
            'title': 'Test Item',
            'description': 'Test',
            'price': '100.00',
        })

        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(SellingPost.objects.count(), 0)

    def test_view_selling_post_detail(self):
        """Test viewing selling post detail page"""
        post = SellingPost.objects.create(
            title='Test Item',
            description='Test description',
            price=Decimal('50.00'),
            seller=self.seller
        )

        response = self.client.get(reverse('marketplace:selling_post_detail', args=[post.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
        self.assertContains(response, 'Test description')
        self.assertContains(response, '50.00')

    def test_commit_to_buy(self):
        """Test buyer committing to purchase"""
        post = SellingPost.objects.create(
            title='Test Item',
            description='Test',
            price=Decimal('50.00'),
            seller=self.seller
        )

        self.client.login(username='buyer', password='testpass123')
        response = self.client.post(reverse('marketplace:commit_to_buy', args=[post.pk]))

        self.assertEqual(response.status_code, 302)  # Redirect

        post.refresh_from_db()
        self.assertTrue(post.is_sold)
        self.assertEqual(post.buyer, self.buyer)

    def test_seller_cannot_buy_own_item(self):
        """Test that seller cannot buy their own item"""
        post = SellingPost.objects.create(
            title='Test Item',
            description='Test',
            price=Decimal('50.00'),
            seller=self.seller
        )

        self.client.login(username='seller', password='testpass123')
        response = self.client.post(reverse('marketplace:commit_to_buy', args=[post.pk]))

        post.refresh_from_db()
        self.assertFalse(post.is_sold)
        self.assertIsNone(post.buyer)

    def test_cannot_buy_already_sold_item(self):
        """Test that already sold items cannot be purchased"""
        post = SellingPost.objects.create(
            title='Test Item',
            description='Test',
            price=Decimal('50.00'),
            seller=self.seller,
            is_sold=True,
            buyer=self.buyer
        )

        other_buyer = User.objects.create_user(username='buyer2', password='testpass123')
        self.client.login(username='buyer2', password='testpass123')
        response = self.client.post(reverse('marketplace:commit_to_buy', args=[post.pk]))

        post.refresh_from_db()
        self.assertEqual(post.buyer, self.buyer)  # Original buyer unchanged


# ===== BUYING POST TESTS =====

class BuyingPostModelTest(TestCase):
    """Test the BuyingPost model"""

    def setUp(self):
        self.buyer = User.objects.create_user(username='buyer', password='testpass123')

    def test_buying_post_creation(self):
        """Test creating a BuyingPost (wanted ad)"""
        post = BuyingPost.objects.create(
            title='Looking for MacBook Pro',
            description='Need 16-inch model',
            min_price=Decimal('1200.00'),
            buyer=self.buyer
        )

        self.assertEqual(post.title, 'Looking for MacBook Pro')
        self.assertEqual(post.min_price, Decimal('1200.00'))
        self.assertEqual(post.buyer, self.buyer)

    def test_buying_post_string_representation(self):
        """Test __str__ method"""
        post = BuyingPost.objects.create(
            title='Want iPhone',
            description='Test',
            min_price=Decimal('400.00'),
            buyer=self.buyer
        )
        self.assertEqual(str(post), 'Want iPhone')


class BuyingPostViewTest(TestCase):
    """Test BuyingPost CRUD views"""

    def setUp(self):
        self.client = Client()
        self.buyer = User.objects.create_user(username='buyer', password='testpass123')

    def test_create_buying_post_authenticated(self):
        """Test creating a buying post when logged in"""
        self.client.login(username='buyer', password='testpass123')

        response = self.client.post(reverse('marketplace:create_buying_post'), {
            'title': 'Looking for PS5',
            'description': 'Looking to buy PS5 console',
            'min_price': '400.00',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(BuyingPost.objects.count(), 1)

        post = BuyingPost.objects.first()
        self.assertEqual(post.title, 'Looking for PS5')
        self.assertEqual(post.min_price, Decimal('400.00'))
        self.assertEqual(post.buyer, self.buyer)

    def test_create_buying_post_unauthenticated(self):
        """Test that unauthenticated users cannot create wanted ads"""
        response = self.client.post(reverse('marketplace:create_buying_post'), {
            'title': 'Test',
            'description': 'Test',
            'min_price': '100.00',
        })

        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(BuyingPost.objects.count(), 0)

    def test_buying_posts_appear_in_feed(self):
        """Test that buying posts appear in marketplace feed"""
        BuyingPost.objects.create(
            title='Want Nintendo Switch',
            description='Looking for Switch',
            min_price=Decimal('250.00'),
            buyer=self.buyer
        )

        response = self.client.get(reverse('marketplace:marketplace_feed'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Want Nintendo Switch')


# ===== MARKET COMMENT TESTS =====

class MarketCommentModelTest(TestCase):
    """Test the MarketComment model"""

    def setUp(self):
        self.seller = User.objects.create_user(username='seller', password='testpass123')
        self.commenter = User.objects.create_user(username='commenter', password='testpass123')
        self.post = SellingPost.objects.create(
            title='Test Item',
            description='Test',
            price=Decimal('100.00'),
            seller=self.seller
        )

    def test_comment_creation(self):
        """Test creating a comment"""
        comment = MarketComment.objects.create(
            post=self.post,
            author=self.commenter,
            content='Is this still available?'
        )

        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.commenter)
        self.assertEqual(comment.content, 'Is this still available?')

    def test_comment_string_representation(self):
        """Test __str__ method"""
        comment = MarketComment.objects.create(
            post=self.post,
            author=self.commenter,
            content='Test comment'
        )
        expected = f'Comment by {self.commenter.username} on {self.post.title}'
        self.assertEqual(str(comment), expected)

    def test_comment_deletion_with_post(self):
        """Test that comments are deleted when post is deleted"""
        comment = MarketComment.objects.create(
            post=self.post,
            author=self.commenter,
            content='Test comment'
        )

        self.post.delete()

        # Comment should be deleted due to CASCADE
        self.assertEqual(MarketComment.objects.count(), 0)


# ===== NOTIFICATION TESTS =====

class NotificationModelTest(TestCase):
    """Test the Notification model"""

    def setUp(self):
        self.seller = User.objects.create_user(username='seller', password='testpass123')
        self.buyer = User.objects.create_user(username='buyer', password='testpass123')

    def test_notification_creation(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            recipient=self.seller,
            sender=self.buyer,
            notification_type='purchase',
            message='Your item has been purchased'
        )

        self.assertEqual(notification.recipient, self.seller)
        self.assertEqual(notification.sender, self.buyer)
        self.assertEqual(notification.notification_type, 'purchase')
        self.assertFalse(notification.is_read)

    def test_notification_types(self):
        """Test different notification types"""
        types = ['purchase', 'bid', 'bid_accepted']

        for notif_type in types:
            notification = Notification.objects.create(
                recipient=self.seller,
                sender=self.buyer,
                notification_type=notif_type,
                message=f'Test {notif_type}'
            )
            self.assertEqual(notification.notification_type, notif_type)

    def test_notification_string_representation(self):
        """Test __str__ method"""
        notification = Notification.objects.create(
            recipient=self.seller,
            sender=self.buyer,
            notification_type='purchase',
            message='Test'
        )
        expected = f"purchase notification from {self.buyer.username} to {self.seller.username}"
        self.assertEqual(str(notification), expected)

    def test_notification_ordering(self):
        """Test that notifications are ordered by creation date (newest first)"""
        notif1 = Notification.objects.create(
            recipient=self.seller,
            sender=self.buyer,
            notification_type='purchase',
            message='First'
        )

        # Small delay to ensure different timestamps
        import time
        time.sleep(0.01)

        notif2 = Notification.objects.create(
            recipient=self.seller,
            sender=self.buyer,
            notification_type='bid',
            message='Second'
        )

        notifications = list(Notification.objects.all())
        self.assertEqual(notifications[0], notif2)  # Newer first
        self.assertEqual(notifications[1], notif1)


class NotificationViewTest(TestCase):
    """Test Notification CRUD views"""

    def setUp(self):
        self.client = Client()
        self.seller = User.objects.create_user(username='seller', password='testpass123')
        self.buyer = User.objects.create_user(username='buyer', password='testpass123')

    def test_notification_created_on_purchase(self):
        """Test that notification is automatically created when item is purchased"""
        post = SellingPost.objects.create(
            title='Test Item',
            description='Test',
            price=Decimal('50.00'),
            seller=self.seller
        )

        self.client.login(username='buyer', password='testpass123')
        self.client.post(reverse('marketplace:commit_to_buy', args=[post.pk]))

        # Should have created a notification
        self.assertEqual(Notification.objects.count(), 1)

        notification = Notification.objects.first()
        self.assertEqual(notification.recipient, self.seller)
        self.assertEqual(notification.sender, self.buyer)
        self.assertEqual(notification.notification_type, 'purchase')
        self.assertEqual(notification.related_selling_post, post)

    def test_view_notifications(self):
        """Test viewing notifications page"""
        notification = Notification.objects.create(
            recipient=self.seller,
            sender=self.buyer,
            notification_type='purchase',
            message='Test notification'
        )

        self.client.login(username='seller', password='testpass123')
        response = self.client.get(reverse('marketplace:notifications'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test notification')

    def test_mark_notification_as_read(self):
        """Test marking a notification as read"""
        notification = Notification.objects.create(
            recipient=self.seller,
            sender=self.buyer,
            notification_type='purchase',
            message='Test notification'
        )

        self.assertFalse(notification.is_read)

        self.client.login(username='seller', password='testpass123')
        response = self.client.post(reverse('marketplace:mark_notification_read', args=[notification.pk]))

        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_cannot_mark_others_notification_as_read(self):
        """Test that users cannot mark other users' notifications as read"""
        notification = Notification.objects.create(
            recipient=self.seller,
            sender=self.buyer,
            notification_type='purchase',
            message='Test notification'
        )

        # Try to mark as read by a different user
        other_user = User.objects.create_user(username='other', password='testpass123')
        self.client.login(username='other', password='testpass123')
        response = self.client.post(reverse('marketplace:mark_notification_read', args=[notification.pk]))

        notification.refresh_from_db()
        self.assertFalse(notification.is_read)

    def test_notification_related_to_listing(self):
        """Test notification with related listing"""
        listing = Listing.objects.create(
            title='Test Auction',
            starting_price=Decimal('50.00'),
            seller=self.seller
        )

        notification = Notification.objects.create(
            recipient=self.seller,
            sender=self.buyer,
            notification_type='bid',
            message='New bid on your auction',
            related_listing=listing
        )

        self.assertEqual(notification.related_listing, listing)


# ===== MARKETPLACE FEED INTEGRATION TESTS =====

class MarketplaceFeedTest(TestCase):
    """Test the complete marketplace feed"""

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')

    def test_feed_displays_all_post_types(self):
        """Test that feed displays selling posts, buying posts, and listings"""
        # Create one of each type
        selling_post = SellingPost.objects.create(
            title='For Sale: Laptop',
            description='Gaming laptop',
            price=Decimal('800.00'),
            seller=self.user1
        )

        buying_post = BuyingPost.objects.create(
            title='Want: iPhone',
            description='Looking for iPhone',
            min_price=Decimal('500.00'),
            buyer=self.user1
        )

        listing = Listing.objects.create(
            title='Auction: Camera',
            description='Vintage camera',
            starting_price=Decimal('100.00'),
            seller=self.user1
        )

        response = self.client.get(reverse('marketplace:marketplace_feed'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'For Sale: Laptop')
        self.assertContains(response, 'Want: iPhone')
        self.assertContains(response, 'Auction: Camera')

    def test_my_listings_tab_shows_user_items(self):
        """Test that My Listings tab shows user's items"""
        self.client.login(username='user1', password='testpass123')

        # Create items for user1
        SellingPost.objects.create(
            title='My Selling Post',
            description='Test',
            price=Decimal('50.00'),
            seller=self.user1
        )

        BuyingPost.objects.create(
            title='My Buying Post',
            description='Test',
            min_price=Decimal('100.00'),
            buyer=self.user1
        )

        Listing.objects.create(
            title='My Auction',
            description='Test',
            starting_price=Decimal('75.00'),
            seller=self.user1
        )

        # Create item for user2 (should not appear)
        SellingPost.objects.create(
            title='Other User Item',
            description='Test',
            price=Decimal('25.00'),
            seller=self.user2
        )

        response = self.client.get(reverse('marketplace:marketplace_feed'))

        self.assertContains(response, 'My Selling Post')
        self.assertContains(response, 'My Buying Post')
        self.assertContains(response, 'My Auction')
        # User2's item should not be in My Listings context
        context = response.context
        self.assertEqual(context['my_selling_posts'].count(), 1)
        self.assertEqual(context['my_buying_posts'].count(), 1)
        self.assertEqual(context['my_listings'].count(), 1)


# ===== ACCEPTANCE BID TESTS =====

class AcceptBidTest(TestCase):
    """Test accepting bids on auctions"""

    def setUp(self):
        self.client = Client()
        self.seller = User.objects.create_user(username='seller', password='testpass123')
        self.bidder = User.objects.create_user(username='bidder', password='testpass123')

        self.listing = Listing.objects.create(
            title='Test Auction',
            starting_price=Decimal('50.00'),
            seller=self.seller
        )

        self.bid = Bid.objects.create(
            listing=self.listing,
            bidder=self.bidder,
            amount=Decimal('75.00')
        )

    def test_seller_can_accept_bid(self):
        """Test that seller can accept a bid"""
        self.client.login(username='seller', password='testpass123')

        response = self.client.post(
            reverse('marketplace:accept_bid', args=[self.listing.pk, self.bid.pk])
        )

        self.assertEqual(response.status_code, 302)

        self.listing.refresh_from_db()
        self.assertTrue(self.listing.is_sold)
        self.assertEqual(self.listing.accepted_bid, self.bid)

    def test_non_seller_cannot_accept_bid(self):
        """Test that non-sellers cannot accept bids"""
        other_user = User.objects.create_user(username='other', password='testpass123')
        self.client.login(username='other', password='testpass123')

        response = self.client.post(
            reverse('marketplace:accept_bid', args=[self.listing.pk, self.bid.pk])
        )

        self.listing.refresh_from_db()
        self.assertFalse(self.listing.is_sold)
        self.assertIsNone(self.listing.accepted_bid)

    def test_notification_created_when_bid_accepted(self):
        """Test that notification is created when bid is accepted"""
        self.client.login(username='seller', password='testpass123')

        self.client.post(
            reverse('marketplace:accept_bid', args=[self.listing.pk, self.bid.pk])
        )

        # Should have created a notification for the bidder
        notifications = Notification.objects.filter(
            recipient=self.bidder,
            notification_type='bid_accepted'
        )
        self.assertEqual(notifications.count(), 1)

