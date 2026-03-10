from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import TextInput

from .models import User
from .widgets import PasswordInputFieldWidget


class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget = PasswordInputFieldWidget()
        self.fields["password2"].widget = PasswordInputFieldWidget()

    def clean_username(self):
        username = self.cleaned_data["username"]
        return username.lower()

    def clean_email(self):
        return self.cleaned_data.get('email').lower()


class AdminAuthenticationFormWithOTP(forms.Form):
    username = forms.CharField(
        max_length=254,
        widget=TextInput(attrs={"autofocus": "autofocus", "placeholder": "Username"}),
    )
    password = forms.CharField(
        widget=PasswordInputFieldWidget(attrs={"placeholder": "Password"})
    )


class OTPVerificationForm(forms.Form):

    def __init__(self, *args, digits=6, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["otp_token"].max_length = digits
        self.fields["otp_token"].widget = TextInput(
            attrs={
                "autofocus": "autofocus",
                "placeholder": f"{digits}-digit OTP",
                "maxlength": digits,
            }
        )

    otp_token = forms.CharField(
        required=True,
        label="MFA Code",
    )
