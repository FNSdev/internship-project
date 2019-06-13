from django import forms
from django.contrib.auth.forms import UserCreationForm
from user.models import User


class RegisterForm(UserCreationForm):
    phone_number = forms.CharField(max_length=13)
    date_of_birth = forms.DateField(widget=forms.DateInput())

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'date_of_birth',)

    def clean_phone_number(self):
        correct_codes = ('+37533', '+37544', '+37529', '+37524', '+37525')
        data = self.cleaned_data['phone_number']
        code = data[:6]
        if not data[6:].isnumeric() or len(data) != 13 or code not in correct_codes:
            raise forms.ValidationError('Phone number is not correct')

        return data


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=150)
    password = forms.CharField(max_length=128, widget=forms.PasswordInput)
