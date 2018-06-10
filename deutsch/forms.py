from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, required=False, help_text='Optional.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

    #def clean_username(self):
    #    print 'Here'
    #    username = self.cleaned_data['username']
    #    print username
    #    user_exists = User.objects.filter(username=username).exists()
    #    #user_exists = User.objects.get(username=username)
    #    print user_exists
    #    if user_exists:
    #        raise ValidationError("User exists")
