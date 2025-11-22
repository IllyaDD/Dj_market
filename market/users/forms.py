from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser



class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("name", "surname", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.save()
        return user


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'surname']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.fields, 'FIELDS DATA')
        self.fields['email'].disabled = True