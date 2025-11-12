from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import (
    CustomUserCreationForm, UserProfileForm, SecurityQuestionForm, 
    SecurityAnswerForm, CustomPasswordResetForm
)
from .models import UserProfile
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create user profile with security questions
            profile = UserProfile.objects.create(
                user=user,
                security_question_1=request.POST.get('question_1'),
                security_answer_1=request.POST.get('answer_1').lower(),
                security_question_2=request.POST.get('question_2'),
                security_answer_2=request.POST.get('answer_2').lower(),
                security_question_3=request.POST.get('question_3'),
                security_answer_3=request.POST.get('answer_3').lower()
            )
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    # Add security questions to context
    security_questions = UserProfile.SECURITY_QUESTIONS
    
    return render(request, 'profiles/signup.html', {
        'form': form,
        'security_questions': security_questions
    })

@login_required
def profile_view(request):
    # Create profile if it doesn't exist
    if not hasattr(request.user, 'userprofile'):
        UserProfile.objects.create(user=request.user)
        
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    
    return render(request, 'profiles/profile.html', {'form': form})

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'profiles/password_change.html', {'form': form})

def security_question_reset(request):
    if request.method == 'POST':
        form = SecurityQuestionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                profile = user.userprofile
                
                # Store username in session for verification
                request.session['reset_username'] = username
                
                # Prepare security questions for verification
                security_questions = [
                    profile.security_question_1,
                    profile.security_question_2,
                    profile.security_question_3,
                ]
                request.session['security_questions'] = security_questions
                
                return redirect('security_question_verify')
            except User.DoesNotExist:
                messages.error(request, 'User with this username does not exist.')
    else:
        form = SecurityQuestionForm()
    
    return render(request, 'profiles/security_question_reset.html', {'form': form})

def security_question_verify(request):
    if 'reset_username' not in request.session or 'security_questions' not in request.session:
        return redirect('security_question_reset')
    
    username = request.session['reset_username']
    security_questions = request.session['security_questions']
    
    if request.method == 'POST':
        form = SecurityAnswerForm(request.POST, questions=security_questions)
        if form.is_valid():
            user = User.objects.get(username=username)
            profile = user.userprofile
            
            # Verify answers (case-insensitive)
            answers_correct = (
                form.cleaned_data['answer_1'].lower() == profile.security_answer_1 and
                form.cleaned_data['answer_2'].lower() == profile.security_answer_2 and
                form.cleaned_data['answer_3'].lower() == profile.security_answer_3
            )
            
            if answers_correct:
                request.session['verified_user'] = username
                return redirect('password_reset_from_questions')
            else:
                messages.error(request, 'One or more security answers are incorrect.')
    else:
        form = SecurityAnswerForm(questions=security_questions)
    
    return render(request, 'profiles/security_question_verify.html', {
        'security_questions': security_questions,
        'form': form
    })

def password_reset_from_questions(request):
    if 'verified_user' not in request.session:
        return redirect('security_question_reset')
    
    username = request.session['verified_user']
    
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=username)
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            
            # Clear session data
            for key in ['reset_username', 'security_questions', 'verified_user']:
                if key in request.session:
                    del request.session[key]
            
            messages.success(request, 'Your password has been reset successfully. You can now log in with your new password.')
            return redirect('login')
    else:
        form = CustomPasswordResetForm()
    
    return render(request, 'profiles/password_reset_from_questions.html', {'form': form})

# Custom login view to use our template
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'profiles/login.html'
    authentication_form = AuthenticationForm