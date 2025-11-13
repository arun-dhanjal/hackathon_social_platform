from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.utils import timezone
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
    now = timezone.now()

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

        edit_form = HostEventForm(instance=event)
    else:
        edit_form = HostEventForm()

    return render(request, "events/event_detail.html", {
        "event": event,
        "user_booking": user_booking,
        "edit_form": edit_form,
        "now": now,
    })


@login_required
def book_event(request, slug):
    """
    Make a booking for an event
    """
    event = get_object_or_404(Event, slug=slug)

    if request.method == "POST":
        # Check if user has already booked this event
        if Booking.objects.filter(event=event, user=request.user).exists():
            messages.info(request, "You already booked this event.")
            return redirect('events:event_detail', slug=event.slug)

        # Create booking
        Booking.objects.create(user=request.user, event=event)

    messages.success(request, "Your booking was successful!")
    return redirect('events:event_detail', slug=slug)


@login_required
def cancel_event(request, slug, booking_id):
    """
    Cancel a booking (booking_id) for the event by the current user.
    """
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        event__slug=slug,
        user=request.user,
    )

    if request.method == 'POST':
        booking.delete()
        messages.success(request, "Your booking has been cancelled.")
        return redirect('events:event_detail', slug=slug)

    return redirect('events:event_detail', slug=slug)


@login_required
def edit_event(request, slug):
    """
    In the event detail page:
        - Show modal which includes edit form for the event
    """
    event = get_object_or_404(Event, slug=slug, host=request.user)

    if request.method == 'POST':

        form = HostEventForm(request.POST, request.FILES, instance=event)

        if form.is_valid():

            updated = form.save(commit=False)

            # Always publish edits (remove draft functionality)
            updated.status = 1

            updated.save()
            messages.success(request, "Event updated.")
            return redirect('events:event_detail', slug=event.slug)
        else:
            # Fall through to re-render page with modal and errors
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = HostEventForm(instance=event)

    return render(
        request,
        'events/event_detail.html',
        {'event': event,
         'edit_form': form,
         'show_edit_modal': True},
    )


@login_required
def delete_event(request, slug):
    """
    Delete an event owned by the current user (host).
    """
    event = get_object_or_404(Event, slug=slug, host=request.user)

    if request.method == 'POST':
        event.delete()
        messages.success(request,
                         f"Your event '{event.title}' has been deleted.")
        return redirect('events:my_events')


@login_required
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

    # Drafts removed: treat all hosted events as published
    published_events = hosted_events.filter(date__gte=now)

    # Booked Events
    booked_upcoming = Booking.objects.filter(
        user=request.user,
        event__status=1,
        event__date__gte=now
    ).select_related('event').order_by('event__date')

    # Past Events
    booked_past = Booking.objects.filter(
        user=request.user,
        event__status=1,
        event__date__lt=now).select_related('event').order_by('event__date')

    # Host Event Form
    event_form = HostEventForm()

    if request.method == "POST":
        event_form = HostEventForm(request.POST, request.FILES)

        if event_form.is_valid():
            event = event_form.save(commit=False)
            event.host = request.user

            # Always publish newly created events; remove draft option
            event.status = 1
            event.save()
            messages.success(request, "Your event has been created.")
            return redirect('events:my_events')
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
            'event_form': event_form,
            'booked_upcoming': booked_upcoming,
            'booked_past': booked_past,
        },
    )
