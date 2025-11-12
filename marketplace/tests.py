from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from threading import Thread
from time import sleep
from .models import Listing, Bid


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
        self.assertContains(response, '$10')

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

