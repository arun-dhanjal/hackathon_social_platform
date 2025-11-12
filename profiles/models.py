from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    # Security Questions
    SECURITY_QUESTIONS = [
        ('What was the name of your first pet?', 'What was the name of your first pet?'),
        ('What is your mother\'s maiden name?', 'What is your mother\'s maiden name?'),
        ('What city were you born in?', 'What city were you born in?'),
        ('What was your high school mascot?', 'What was your high school mascot?'),
        ('What is the name of your favorite childhood friend?', 'What is the name of your favorite childhood friend?'),
        ('What was the make of your first car?', 'What was the make of your first car?'),
        ('What is your favorite book?', 'What is your favorite book?'),
        ('What is your favorite movie?', 'What is your favorite movie?'),
    ]
    
    security_question_1 = models.CharField(max_length=200, choices=SECURITY_QUESTIONS)
    security_answer_1 = models.CharField(max_length=100)
    
    security_question_2 = models.CharField(max_length=200, choices=SECURITY_QUESTIONS)
    security_answer_2 = models.CharField(max_length=100)
    
    security_question_3 = models.CharField(max_length=200, choices=SECURITY_QUESTIONS)
    security_answer_3 = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"