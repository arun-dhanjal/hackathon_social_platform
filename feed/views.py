from django.shortcuts import render, redirect


def home(request):
    """Home page - redirect to marketplace"""
    return redirect('marketplace:marketplace_feed')


def feed(request):
    """Social feed placeholder"""
    return render(request, 'feed/feed.html', {})
