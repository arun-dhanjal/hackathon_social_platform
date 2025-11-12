from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'birth_date', 'profile_picture']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class SecurityQuestionForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)

class SecurityAnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions', [])
        super(SecurityAnswerForm, self).__init__(*args, **kwargs)
        
        for i, question in enumerate(questions, 1):
            self.fields[f'answer_{i}'] = forms.CharField(
                label=question,
                max_length=100,
                required=True
            )

class CustomPasswordResetForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data