from django.urls import path
from django.http import HttpResponse

def dummy_marketplace_view(request):
	return HttpResponse("Dummy marketplace view")

urlpatterns = [
	path('dummy/', dummy_marketplace_view, name='marketplace'),
]
