from django.urls import path
from django.http import HttpResponse

def dummy_events_view(request):
	return HttpResponse("Dummy events view")

urlpatterns = [
	path('dummy/', dummy_events_view, name='events'),
]
