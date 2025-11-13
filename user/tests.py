from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile


class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='Test bio',
            location='Test City',
            security_question_1='What city were you born in?',
            security_answer_1='test city',
            security_question_2='What was the name of your first pet?',
            security_answer_2='test pet',
            security_question_3='What is your favorite book?',
            security_answer_3='test book'
        )
    
    def test_user_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.bio, 'Test bio')
        self.assertTrue(isinstance(self.profile, UserProfile))
        self.assertEqual(str(self.profile), "testuser's Profile")
    
    def test_user_profile_security_questions(self):
        self.assertEqual(self.profile.security_question_1, 'What city were you born in?')
        self.assertEqual(self.profile.security_answer_1, 'test city')


class UserViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            security_question_1='What city were you born in?',
            security_answer_1='test city',
            security_question_2='What was the name of your first pet?',
            security_answer_2='test pet',
            security_question_3='What is your favorite book?',
            security_answer_3='test book'
        )
    
    def test_login_view(self):
        response = self.client.get(reverse('user:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')
    
    def test_signup_view_get(self):
        response = self.client.get(reverse('user:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/signup.html')
    
    def test_profile_view_requires_login(self):
        response = self.client.get(reverse('user:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')


class UserFormTests(TestCase):
    def test_valid_signup_form(self):
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        }
        # This would need additional security question data in actual test
        # For now, just testing basic form validation
        from .forms import CustomUserCreationForm
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())