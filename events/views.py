from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.utils import timezone
from django.http import HttpResponseRedirect
from .forms import HostEventForm
from .models import Event, Booking


# Create your views here.

class EventsList(generic.ListView):
    # Current time
    now = timezone.now()

    queryset = Event.objects.filter(status=1, date__gte=now).order_by('date')
    template_name = "events/index.html"
    paginate_by = 6


def event_detail(request, slug):
    """
    Display the event details in its own page
    """
    # Current time
    # now = timezone.now()

    event = get_object_or_404(Event, slug=slug)

    # If the user is authenticated, check whether they
    # have a booking for this event
    user_booking = None
    if request.user.is_authenticated:
        user_booking = (
            Booking.objects
            .filter(event=event, user=request.user)
            .first()
        )

    return render(request, "events/event_detail.html", {
        "event": event,
        "user_booking": user_booking,
    })


def my_events(request):
    """
    Render the My Events page
    Handles:
        - Hosting event
        - View booked & booked past events
    """
    # Current time
    now = timezone.now()

    # Hosted Events
    hosted_events = Event.objects.filter(
        host=request.user
        ).order_by('-created_on')

    draft_events = hosted_events.filter(status=0)
    published_events = hosted_events.filter(status=1, date__gte=now)

    # Booked Events
    booked_upcoming = Booking.objects.filter(
        user=request.user,
        event__status=1,
        event__date__gte=now
    ).select_related('event').order_by('event__date')

    # Host Event Form
    event_form = HostEventForm()

    if request.method == "POST":
        event_form = HostEventForm(request.POST, request.FILES)

        if event_form.is_valid():
            event = event_form.save(commit=False)
            event.host = request.user

            if 'publish' in request.POST:
                event.status = 1
                messages.success(request, "Your event has been published!")
            else:
                event.status = 0
                messages.info(request, "Event saved as draft.")

            event.save()
            return redirect('my_events')
        else:
            messages.error(
                request,
                "There was an error with your form. "
                "Please check your fields.")

    return render(
        request,
        "events/my_events.html",
        {
            'published_events': published_events,
            'draft_events': draft_events,
            'event_form': event_form,
            'booked_upcoming': booked_upcoming,
        },
    )


def book_event(request, slug):
    """
    Make a booking for an event
    """
    event = get_object_or_404(Event, slug=slug)

    if request.method == "POST":
        # Check if user has already booked this event
        if Booking.objects.filter(event=event, user=request.user).exists():
            messages.info(request, "You already booked this event.")
            return redirect('event_detail', slug=event.slug)
        
        # Create booking
        Booking.objects.create(user=request.user, event=event)

    messages.success(request, "Your booking was successful!")
    return HttpResponseRedirect(reverse('event_detail', args=[slug]))
