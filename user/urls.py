from django.urls import path
from django.http import HttpResponse

def dummy_user_view(request):
	return HttpResponse("Dummy user view")

urlpatterns = [
	path('dummy/', dummy_user_view, name='user'),
]
