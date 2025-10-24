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

# New form for editing users
class UserEditForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'username', 'email', 'role']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # The logged-in user
        super().__init__(*args, **kwargs)
        # Exclude role field if not admin or if editing self (admins can't change own role)
        if not self.user or self.user.role != Users.Role.ADMIN or (self.instance and self.instance.id == self.user.id):
            self.fields.pop('role', None)
        else:
            # Limit role choices for security
            self.fields['role'].choices = [(Users.Role.LIBRARIAN, 'Librarian'), (Users.Role.USER, 'User')]

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            first_name = first_name.strip().title()
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            last_name = last_name.strip().title()
        return last_name
