from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import UserProfile
from .forms import CustomUserCreationForm, UserProfileForm, SecurityQuestionForm, SecurityAnswerForm, CustomPasswordResetForm


# ===== MODEL TESTS =====

class UserProfileModelTests(TestCase):
    """Test the UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Profile is auto-created by signal, just get and update it
        self.profile = self.user.userprofile
        self.profile.bio = 'Test bio'
        self.profile.location = 'Test City'
        self.profile.security_question_1 = 'What city were you born in?'
        self.profile.security_answer_1 = 'test city'
        self.profile.security_question_2 = 'What was the name of your first pet?'
        self.profile.security_answer_2 = 'test pet'
        self.profile.security_question_3 = 'What is your favorite book?'
        self.profile.security_answer_3 = 'test book'
        self.profile.save()
    
    def test_user_profile_creation(self):
        """Test creating a user profile"""
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.bio, 'Test bio')
        self.assertEqual(self.profile.location, 'Test City')
        self.assertTrue(isinstance(self.profile, UserProfile))
        
    def test_user_profile_string_representation(self):
        """Test __str__ method"""
        self.assertEqual(str(self.profile), "testuser's Profile")
    
    def test_user_profile_security_questions(self):
        """Test security questions are stored correctly"""
        self.assertEqual(self.profile.security_question_1, 'What city were you born in?')
        self.assertEqual(self.profile.security_answer_1, 'test city')
        self.assertEqual(self.profile.security_question_2, 'What was the name of your first pet?')
        self.assertEqual(self.profile.security_answer_2, 'test pet')
        self.assertEqual(self.profile.security_question_3, 'What is your favorite book?')
        self.assertEqual(self.profile.security_answer_3, 'test book')
        
    def test_user_profile_optional_fields(self):
        """Test that optional fields can be blank"""
        user2 = User.objects.create_user(username='user2', password='pass123')
        profile = user2.userprofile  # Get auto-created profile
        profile.security_question_1 = 'Question 1'
        profile.security_answer_1 = 'answer1'
        profile.security_question_2 = 'Question 2'
        profile.security_answer_2 = 'answer2'
        profile.security_question_3 = 'Question 3'
        profile.security_answer_3 = 'answer3'
        profile.save()
        
        self.assertEqual(profile.bio, '')
        self.assertEqual(profile.location, '')
        self.assertIsNone(profile.birth_date)
        
    def test_user_profile_social_media_fields(self):
        """Test social media URL fields"""
        self.profile.website = 'https://example.com'
        self.profile.github = 'https://github.com/testuser'
        self.profile.twitter = 'https://twitter.com/testuser'
        self.profile.linkedin = 'https://linkedin.com/in/testuser'
        self.profile.save()
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.website, 'https://example.com')
        self.assertEqual(self.profile.github, 'https://github.com/testuser')
        
    def test_user_profile_default_values(self):
        """Test default field values"""
        user3 = User.objects.create_user(username='user3', password='pass123')
        profile = user3.userprofile  # Get auto-created profile
        profile.security_question_1 = 'Q1'
        profile.security_answer_1 = 'a1'
        profile.security_question_2 = 'Q2'
        profile.security_answer_2 = 'a2'
        profile.security_question_3 = 'Q3'
        profile.security_answer_3 = 'a3'
        profile.save()
        
        self.assertFalse(profile.is_verified)
        self.assertIsNotNone(profile.date_joined)
        self.assertIsNotNone(profile.last_active)
        
    def test_user_profile_cascade_deletion(self):
        """Test that profile is deleted when user is deleted"""
        self.user.delete()
        self.assertEqual(UserProfile.objects.count(), 0)


# ===== VIEW TESTS =====

class LoginViewTests(TestCase):
    """Test the login view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_view_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(reverse('user:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')
        
    def test_login_with_valid_credentials(self):
        """Test login with correct credentials"""
        response = self.client.post(reverse('user:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        
    def test_login_with_invalid_credentials(self):
        """Test login with incorrect credentials"""
        response = self.client.post(reverse('user:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class SignupViewTests(TestCase):
    """Test the signup view"""
    
    def setUp(self):
        self.client = Client()
    
    def test_signup_view_loads(self):
        """Test that signup page loads successfully"""
        response = self.client.get(reverse('user:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/signup.html')
        
    def test_signup_creates_user_and_profile(self):
        """Test that signup creates both user and profile"""
        response = self.client.post(reverse('user:signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'question_1': 'What city were you born in?',
            'answer_1': 'London',
            'question_2': 'What was the name of your first pet?',
            'answer_2': 'Fluffy',
            'question_3': 'What is your favorite book?',
            'answer_3': 'Python Guide',
        })
        
        # Check user was created
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.username, 'newuser')
        
        # Check profile was created
        self.assertEqual(UserProfile.objects.count(), 1)
        profile = UserProfile.objects.first()
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.security_answer_1, 'london')  # Should be lowercase
        
    def test_signup_logs_user_in(self):
        """Test that signup automatically logs user in"""
        self.client.post(reverse('user:signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'question_1': 'What city were you born in?',
            'answer_1': 'London',
            'question_2': 'What was the name of your first pet?',
            'answer_2': 'Fluffy',
            'question_3': 'What is your favorite book?',
            'answer_3': 'Python Guide',
        })
        
        # User should be logged in
        response = self.client.get(reverse('user:profile'))
        self.assertEqual(response.status_code, 200)  # Can access protected page


class ProfileViewTests(TestCase):
    """Test the profile view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Get auto-created profile and update it
        self.profile = self.user.userprofile
        self.profile.bio = 'Original bio'
        self.profile.security_question_1 = 'Q1'
        self.profile.security_answer_1 = 'a1'
        self.profile.security_question_2 = 'Q2'
        self.profile.security_answer_2 = 'a2'
        self.profile.security_question_3 = 'Q3'
        self.profile.security_answer_3 = 'a3'
        self.profile.save()
    
    def test_profile_view_requires_login(self):
        """Test that profile page requires authentication"""
        response = self.client.get(reverse('user:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_view_authenticated(self):
        """Test that authenticated users can access profile"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')
        
    def test_profile_update(self):
        """Test updating profile information"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('user:profile'), {
            'bio': 'Updated bio',
            'location': 'New City',
        })
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio')
        self.assertEqual(self.profile.location, 'New City')
        
    def test_profile_auto_creation(self):
        """Test that profile is auto-created by signal when user is created"""
        user_with_profile = User.objects.create_user(
            username='autoprofile',
            password='testpass123'
        )
        
        # Profile should be auto-created by signal
        self.assertTrue(hasattr(user_with_profile, 'userprofile'))
        self.assertIsNotNone(user_with_profile.userprofile)
        
        # Access profile page to confirm it works
        self.client.login(username='autoprofile', password='testpass123')
        response = self.client.get(reverse('user:profile'))
        
        self.assertEqual(response.status_code, 200)


class PasswordChangeViewTests(TestCase):
    """Test the password change view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='oldpassword123'
        )
    
    def test_password_change_requires_login(self):
        """Test that password change requires authentication"""
        response = self.client.get(reverse('user:password_change'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_password_change_view_loads(self):
        """Test that password change page loads for authenticated users"""
        self.client.login(username='testuser', password='oldpassword123')
        response = self.client.get(reverse('user:password_change'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/password_change.html')
        
    def test_password_change_success(self):
        """Test successful password change"""
        self.client.login(username='testuser', password='oldpassword123')
        response = self.client.post(reverse('user:password_change'), {
            'old_password': 'oldpassword123',
            'new_password1': 'NewComplexPass123!',
            'new_password2': 'NewComplexPass123!',
        })
        
        # User should still be logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        
        # New password should work
        self.client.logout()
        login_success = self.client.login(username='testuser', password='NewComplexPass123!')
        self.assertTrue(login_success)


class SecurityQuestionResetTests(TestCase):
    """Test the security question password reset flow"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # Get auto-created profile and update it
        self.profile = self.user.userprofile
        self.profile.security_question_1 = 'What city were you born in?'
        self.profile.security_answer_1 = 'london'
        self.profile.security_question_2 = 'What was the name of your first pet?'
        self.profile.security_answer_2 = 'fluffy'
        self.profile.security_question_3 = 'What is your favorite book?'
        self.profile.security_answer_3 = 'python guide'
        self.profile.save()
    
    def test_security_question_reset_view_loads(self):
        """Test that security question reset page loads"""
        response = self.client.get(reverse('user:security_question_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/security_question_reset.html')
        
    def test_security_question_submit_valid_username(self):
        """Test submitting valid username"""
        response = self.client.post(reverse('user:security_question_reset'), {
            'username': 'testuser'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to verify
        self.assertIn('reset_username', self.client.session)
        self.assertIn('security_questions', self.client.session)
        
    def test_security_question_submit_invalid_username(self):
        """Test submitting invalid username"""
        response = self.client.post(reverse('user:security_question_reset'), {
            'username': 'nonexistent'
        })
        self.assertEqual(response.status_code, 200)  # Stay on page
        self.assertNotIn('reset_username', self.client.session)
        
    def test_security_answer_verification_correct(self):
        """Test correct security answers"""
        # Set up session
        session = self.client.session
        session['reset_username'] = 'testuser'
        session['security_questions'] = [
            self.profile.security_question_1,
            self.profile.security_question_2,
            self.profile.security_question_3
        ]
        session.save()
        
        response = self.client.post(reverse('user:security_question_verify'), {
            'answer_1': 'London',  # Test case-insensitive
            'answer_2': 'Fluffy',
            'answer_3': 'Python Guide'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect to reset password
        self.assertIn('verified_user', self.client.session)
        
    def test_security_answer_verification_incorrect(self):
        """Test incorrect security answers"""
        # Set up session
        session = self.client.session
        session['reset_username'] = 'testuser'
        session['security_questions'] = [
            self.profile.security_question_1,
            self.profile.security_question_2,
            self.profile.security_question_3
        ]
        session.save()
        
        response = self.client.post(reverse('user:security_question_verify'), {
            'answer_1': 'Wrong',
            'answer_2': 'Wrong',
            'answer_3': 'Wrong'
        })
        
        self.assertEqual(response.status_code, 200)  # Stay on page
        self.assertNotIn('verified_user', self.client.session)
        
    def test_password_reset_from_questions(self):
        """Test resetting password after verification"""
        # Set up session as if user passed verification
        session = self.client.session
        session['verified_user'] = 'testuser'
        session.save()
        
        response = self.client.post(reverse('user:password_reset_from_questions'), {
            'new_password': 'NewComplexPass123!',
            'confirm_password': 'NewComplexPass123!'
        })
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        
        # Session should be cleared
        self.assertNotIn('verified_user', self.client.session)
        
        # New password should work
        login_success = self.client.login(username='testuser', password='NewComplexPass123!')
        self.assertTrue(login_success)


class LogoutViewTests(TestCase):
    """Test the logout functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_logout_view(self):
        """Test that logout works correctly"""
        self.client.login(username='testuser', password='testpass123')
        
        # User should be authenticated
        response = self.client.get(reverse('user:profile'))
        self.assertEqual(response.status_code, 200)
        
        # Logout
        response = self.client.post(reverse('user:logout'))
        
        # User should no longer be authenticated
        response = self.client.get(reverse('user:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


# ===== FORM TESTS =====

class CustomUserCreationFormTests(TestCase):
    """Test the custom user creation form"""
    
    def test_valid_signup_form(self):
        """Test form with valid data"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_passwords_must_match(self):
        """Test that passwords must match"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass123!',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_username_must_be_unique(self):
        """Test that username must be unique"""
        User.objects.create_user(username='existing', password='pass123')
        
        form_data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())


class UserProfileFormTests(TestCase):
    """Test the user profile form"""
    
    def test_valid_profile_form(self):
        """Test form with valid data"""
        form_data = {
            'bio': 'Test bio',
            'location': 'Test City',
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_optional_fields(self):
        """Test that fields can be left blank"""
        form_data = {}
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())


class SecurityQuestionFormTests(TestCase):
    """Test the security question form"""
    
    def test_valid_security_question_form(self):
        """Test form with valid username"""
        User.objects.create_user(username='testuser', password='pass123')
        
        form_data = {
            'username': 'testuser'
        }
        form = SecurityQuestionForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_empty_username_invalid(self):
        """Test that empty username is invalid"""
        form_data = {
            'username': ''
        }
        form = SecurityQuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
