from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Event, Booking
from .forms import HostEventForm


# ===== MODEL TESTS =====

class EventModelTest(TestCase):
    """Test the Event model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testhost', password='testpass123')
        self.future_date = timezone.now() + timedelta(days=7)
        
    def test_event_creation(self):
        """Test creating an event"""
        event = Event.objects.create(
            title='Test Event',
            date=self.future_date,
            location='Test Location',
            host=self.user,
            description='Test description',
            status=1
        )
        self.assertEqual(event.title, 'Test Event')
        self.assertEqual(event.location, 'Test Location')
        self.assertEqual(event.host, self.user)
        self.assertEqual(event.status, 1)
        
    def test_event_slug_auto_generation(self):
        """Test that slug is automatically generated from title"""
        event = Event.objects.create(
            title='My Amazing Event',
            date=self.future_date,
            location='Test Location',
            host=self.user,
            status=1
        )
        self.assertEqual(event.slug, 'my-amazing-event')
        
    def test_event_slug_handles_duplicates(self):
        """Test that duplicate titles get unique slugs"""
        event1 = Event.objects.create(
            title='Same Title',
            date=self.future_date,
            location='Location 1',
            host=self.user,
            status=1
        )
        event2 = Event.objects.create(
            title='Same Title',
            date=self.future_date,
            location='Location 2',
            host=self.user,
            status=1
        )
        self.assertEqual(event1.slug, 'same-title')
        self.assertEqual(event2.slug, 'same-title-1')
        
    def test_event_string_representation(self):
        """Test __str__ method"""
        event = Event.objects.create(
            title='Test Event',
            date=self.future_date,
            location='Test Location',
            host=self.user,
            status=1
        )
        expected = f"Test Event | hosted by {self.user.username}"
        self.assertEqual(str(event), expected)
        
    def test_event_ordering(self):
        """Test that events are ordered by date descending"""
        event1 = Event.objects.create(
            title='Event 1',
            date=timezone.now() + timedelta(days=1),
            location='Location',
            host=self.user,
            status=1
        )
        event2 = Event.objects.create(
            title='Event 2',
            date=timezone.now() + timedelta(days=7),
            location='Location',
            host=self.user,
            status=1
        )
        events = list(Event.objects.all())
        self.assertEqual(events[0], event2)  # Later date first
        self.assertEqual(events[1], event1)
        
    def test_event_default_status_is_draft(self):
        """Test that events default to draft status"""
        event = Event.objects.create(
            title='Draft Event',
            date=self.future_date,
            location='Location',
            host=self.user
        )
        self.assertEqual(event.status, 0)


class BookingModelTest(TestCase):
    """Test the Booking model"""
    
    def setUp(self):
        self.host = User.objects.create_user(username='host', password='testpass123')
        self.attendee = User.objects.create_user(username='attendee', password='testpass123')
        self.event = Event.objects.create(
            title='Test Event',
            date=timezone.now() + timedelta(days=7),
            location='Test Location',
            host=self.host,
            status=1
        )
        
    def test_booking_creation(self):
        """Test creating a booking"""
        booking = Booking.objects.create(
            user=self.attendee,
            event=self.event
        )
        self.assertEqual(booking.user, self.attendee)
        self.assertEqual(booking.event, self.event)
        
    def test_booking_string_representation(self):
        """Test __str__ method"""
        booking = Booking.objects.create(
            user=self.attendee,
            event=self.event
        )
        expected = f"{self.event} booked by {self.attendee.username}"
        self.assertEqual(str(booking), expected)
        
    def test_booking_ordering(self):
        """Test that bookings are ordered by booked_at"""
        booking1 = Booking.objects.create(user=self.attendee, event=self.event)
        booking2 = Booking.objects.create(
            user=self.host,
            event=self.event
        )
        bookings = list(Booking.objects.all())
        self.assertEqual(bookings[0], booking1)  # Earlier booking first
        self.assertEqual(bookings[1], booking2)
        
    def test_booking_cascade_deletion_with_event(self):
        """Test that bookings are deleted when event is deleted"""
        booking = Booking.objects.create(
            user=self.attendee,
            event=self.event
        )
        self.event.delete()
        self.assertEqual(Booking.objects.count(), 0)


# ===== VIEW TESTS =====

class EventsListViewTest(TestCase):
    """Test the events list view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
    def test_events_list_view_loads(self):
        """Test that events feed page loads"""
        response = self.client.get(reverse('events:events_feed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/index.html')
        
    def test_events_list_shows_published_future_events(self):
        """Test that published future events appear"""
        event = Event.objects.create(
            title='Future Event',
            date=timezone.now() + timedelta(days=7),
            location='Location',
            host=self.user,
            status=1  # Published
        )
        response = self.client.get(reverse('events:events_feed'))
        self.assertContains(response, 'Future Event')
        
    def test_events_list_hides_draft_events(self):
        """Test that draft events don't appear"""
        event = Event.objects.create(
            title='Draft Event',
            date=timezone.now() + timedelta(days=7),
            location='Location',
            host=self.user,
            status=0  # Draft
        )
        response = self.client.get(reverse('events:events_feed'))
        self.assertNotContains(response, 'Draft Event')
        
    def test_events_list_hides_past_events(self):
        """Test that past events don't appear"""
        event = Event.objects.create(
            title='Past Event',
            date=timezone.now() - timedelta(days=1),
            location='Location',
            host=self.user,
            status=1
        )
        response = self.client.get(reverse('events:events_feed'))
        self.assertNotContains(response, 'Past Event')
        
    def test_events_list_pagination(self):
        """Test pagination with many events"""
        for i in range(10):
            Event.objects.create(
                title=f'Event {i}',
                date=timezone.now() + timedelta(days=i+1),
                location='Location',
                host=self.user,
                status=1
            )
        response = self.client.get(reverse('events:events_feed'))
        self.assertEqual(len(response.context['object_list']), 6)


class EventDetailViewTest(TestCase):
    """Test the event detail view"""
    
    def setUp(self):
        self.client = Client()
        self.host = User.objects.create_user(username='host', password='testpass123')
        self.attendee = User.objects.create_user(username='attendee', password='testpass123')
        self.event = Event.objects.create(
            title='Test Event',
            date=timezone.now() + timedelta(days=7),
            location='Test Location',
            host=self.host,
            description='Event description',
            status=1
        )
        
    def test_event_detail_view_loads(self):
        """Test that event detail page loads"""
        response = self.client.get(reverse('events:event_detail', args=[self.event.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/event_detail.html')
        self.assertContains(response, 'Test Event')
        
    def test_event_detail_shows_booking_status_for_authenticated(self):
        """Test that booking status is shown for logged in users"""
        self.client.login(username='attendee', password='testpass123')
        Booking.objects.create(user=self.attendee, event=self.event)
        
        response = self.client.get(reverse('events:event_detail', args=[self.event.slug]))
        self.assertTrue(response.context['user_booking'])
        
    def test_event_detail_404_for_nonexistent_event(self):
        """Test 404 for non-existent event"""
        response = self.client.get(reverse('events:event_detail', args=['nonexistent-slug']))
        self.assertEqual(response.status_code, 404)


class BookEventViewTest(TestCase):
    """Test the book event functionality"""
    
    def setUp(self):
        self.client = Client()
        self.host = User.objects.create_user(username='host', password='testpass123')
        self.attendee = User.objects.create_user(username='attendee', password='testpass123')
        self.event = Event.objects.create(
            title='Test Event',
            date=timezone.now() + timedelta(days=7),
            location='Test Location',
            host=self.host,
            status=1
        )
        
    def test_book_event_requires_login(self):
        """Test that booking requires authentication"""
        response = self.client.post(reverse('events:book_event', args=[self.event.slug]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(Booking.objects.count(), 0)
        
    def test_book_event_creates_booking(self):
        """Test that booking is created successfully"""
        self.client.login(username='attendee', password='testpass123')
        response = self.client.post(reverse('events:book_event', args=[self.event.slug]))
        
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()
        self.assertEqual(booking.user, self.attendee)
        self.assertEqual(booking.event, self.event)
        
    def test_book_event_prevents_duplicate_bookings(self):
        """Test that users can't book the same event twice"""
        self.client.login(username='attendee', password='testpass123')
        
        # First booking
        self.client.post(reverse('events:book_event', args=[self.event.slug]))
        
        # Second attempt
        self.client.post(reverse('events:book_event', args=[self.event.slug]))
        
        # Should still only have 1 booking
        self.assertEqual(Booking.objects.count(), 1)


class CancelEventViewTest(TestCase):
    """Test the cancel booking functionality"""
    
    def setUp(self):
        self.client = Client()
        self.host = User.objects.create_user(username='host', password='testpass123')
        self.attendee = User.objects.create_user(username='attendee', password='testpass123')
        self.event = Event.objects.create(
            title='Test Event',
            date=timezone.now() + timedelta(days=7),
            location='Test Location',
            host=self.host,
            status=1
        )
        self.booking = Booking.objects.create(user=self.attendee, event=self.event)
        
    def test_cancel_booking_requires_login(self):
        """Test that canceling requires authentication"""
        response = self.client.post(
            reverse('events:cancel_event', args=[self.event.slug, self.booking.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(Booking.objects.count(), 1)  # Booking still exists
        
    def test_cancel_booking_deletes_booking(self):
        """Test that booking is deleted successfully"""
        self.client.login(username='attendee', password='testpass123')
        response = self.client.post(
            reverse('events:cancel_event', args=[self.event.slug, self.booking.id])
        )
        
        self.assertEqual(Booking.objects.count(), 0)
        
    def test_cancel_booking_only_own_booking(self):
        """Test that users can only cancel their own bookings"""
        other_user = User.objects.create_user(username='other', password='testpass123')
        self.client.login(username='other', password='testpass123')
        
        response = self.client.post(
            reverse('events:cancel_event', args=[self.event.slug, self.booking.id])
        )
        
        # Should return 404 as booking doesn't belong to them
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Booking.objects.count(), 1)  # Booking still exists


class MyEventsViewTest(TestCase):
    """Test the my events view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
    def test_my_events_requires_login(self):
        """Test that my events page requires authentication"""
        response = self.client.get(reverse('events:my_events'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_my_events_view_loads(self):
        """Test that my events page loads for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('events:my_events'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events/my_events.html')
        
    def test_my_events_shows_hosted_events(self):
        """Test that user's hosted events appear"""
        self.client.login(username='testuser', password='testpass123')
        event = Event.objects.create(
            title='My Hosted Event',
            date=timezone.now() + timedelta(days=7),
            location='Location',
            host=self.user,
            status=1
        )
        response = self.client.get(reverse('events:my_events'))
        self.assertContains(response, 'My Hosted Event')
        
    def test_my_events_shows_booked_events(self):
        """Test that user's booked events appear"""
        other_host = User.objects.create_user(username='host', password='testpass123')
        event = Event.objects.create(
            title='Booked Event',
            date=timezone.now() + timedelta(days=7),
            location='Location',
            host=other_host,
            status=1
        )
        Booking.objects.create(user=self.user, event=event)
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('events:my_events'))
        self.assertContains(response, 'Booked Event')
        
    def test_create_event_from_my_events(self):
        """Test creating an event from my events page"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('events:my_events'), {
            'title': 'New Event',
            'date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'location': 'New Location',
            'description': 'Description'
        })
        
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first()
        self.assertEqual(event.title, 'New Event')
        self.assertEqual(event.host, self.user)
        self.assertEqual(event.status, 1)  # Auto-published


class EditEventViewTest(TestCase):
    """Test the edit event functionality"""
    
    def setUp(self):
        self.client = Client()
        self.host = User.objects.create_user(username='host', password='testpass123')
        self.other_user = User.objects.create_user(username='other', password='testpass123')
        self.event = Event.objects.create(
            title='Original Title',
            date=timezone.now() + timedelta(days=7),
            location='Original Location',
            host=self.host,
            status=1
        )
        
    def test_edit_event_requires_login(self):
        """Test that editing requires authentication"""
        response = self.client.post(reverse('events:edit_event', args=[self.event.slug]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_edit_event_only_by_host(self):
        """Test that only the host can edit their event"""
        self.client.login(username='other', password='testpass123')
        response = self.client.get(reverse('events:edit_event', args=[self.event.slug]))
        self.assertEqual(response.status_code, 404)
        
    def test_edit_event_updates_event(self):
        """Test that event is updated successfully"""
        self.client.login(username='host', password='testpass123')
        
        response = self.client.post(reverse('events:edit_event', args=[self.event.slug]), {
            'title': 'Updated Title',
            'date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'location': 'Updated Location',
            'description': 'Updated description'
        })
        
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Updated Title')
        self.assertEqual(self.event.location, 'Updated Location')


class DeleteEventViewTest(TestCase):
    """Test the delete event functionality"""
    
    def setUp(self):
        self.client = Client()
        self.host = User.objects.create_user(username='host', password='testpass123')
        self.other_user = User.objects.create_user(username='other', password='testpass123')
        self.event = Event.objects.create(
            title='Event to Delete',
            date=timezone.now() + timedelta(days=7),
            location='Location',
            host=self.host,
            status=1
        )
        
    def test_delete_event_requires_login(self):
        """Test that deleting requires authentication"""
        response = self.client.post(reverse('events:delete_event', args=[self.event.slug]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(Event.objects.count(), 1)  # Event still exists
        
    def test_delete_event_only_by_host(self):
        """Test that only the host can delete their event"""
        self.client.login(username='other', password='testpass123')
        response = self.client.post(reverse('events:delete_event', args=[self.event.slug]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Event.objects.count(), 1)  # Event still exists
        
    def test_delete_event_removes_event(self):
        """Test that event is deleted successfully"""
        self.client.login(username='host', password='testpass123')
        response = self.client.post(reverse('events:delete_event', args=[self.event.slug]))
        
        self.assertEqual(Event.objects.count(), 0)


# ===== FORM TESTS =====

class HostEventFormTest(TestCase):
    """Test the HostEventForm"""
    
    def test_valid_event_form(self):
        """Test valid form data"""
        form_data = {
            'title': 'Test Event',
            'date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'location': 'Test Location',
            'description': 'Test description'
        }
        form = HostEventForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_empty_title_invalid(self):
        """Test that empty title is invalid"""
        form_data = {
            'title': '',
            'date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'location': 'Test Location'
        }
        form = HostEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_empty_date_invalid(self):
        """Test that empty date is invalid"""
        form_data = {
            'title': 'Test Event',
            'date': '',
            'location': 'Test Location'
        }
        form = HostEventForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_empty_location_invalid(self):
        """Test that empty location is invalid"""
        form_data = {
            'title': 'Test Event',
            'date': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'location': ''
        }
        form = HostEventForm(data=form_data)
        self.assertFalse(form.is_valid())
