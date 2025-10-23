from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
from .models import Users

class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Users
        fields = ('username', 'email')

class UserLoginForm(AuthenticationForm):
    pass

class AdminUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=Users.Role.choices)   
    class Meta(UserCreationForm.Meta):
        model = Users
        fields = ('username', 'email', 'role')
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data["role"]      
        if commit:
            user.save()
        return user

class UserProfileChangeForm(UserChangeForm):
    password = None 
    class Meta:
        model = Users
        fields = ('username', 'email')

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = Users

class AdminUserChangeForm(UserChangeForm):
    password = None 
    class Meta:
        model = Users
        fields = (
            'username', 
            'email', 
            'role',
            'is_active', 
            'is_staff', 
            'is_superuser'
        )