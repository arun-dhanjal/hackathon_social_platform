from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='profiles/logout.html'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('password-change/', views.password_change_view, name='password_change'),
    
    # Security Question Password Reset URLs
    path('security-question-reset/', views.security_question_reset, name='security_question_reset'),
    path('security-question-verify/', views.security_question_verify, name='security_question_verify'),
    path('password-reset-from-questions/', views.password_reset_from_questions, name='password_reset_from_questions'),
]