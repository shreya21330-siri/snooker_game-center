
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CustomerRegistrationForm(UserCreationForm):

    name = forms.CharField(
        max_length=100,
        label="Full Name"
    )

    email = forms.EmailField(
        required=True
    )

    phone = forms.CharField(
        max_length=15,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'username',
            'name',
            'email',
            'phone',
            'password1',
            'password2',
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['name']
        user.is_active = False

        if commit:
            user.save()

        return user
