from typing import Any
from django import forms
from .models import Account

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={})
    )

    class Meta:
        model = Account
        fields = ["first_name", "last_name", "email", "phone_number", "password", "confirm_password"]        
        
        
        
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs["class"]='form-control'



    def clean(self):
        cleaned_data=super(RegisterForm, self).clean()
        password=cleaned_data.get("password")
        confirm_password=cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("password does not match")


class LoginForm(forms.Form):  
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"placeholder": "Email Address", 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", 'class': 'form-control'})
    )


class ResetForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"placeholder": "Email Address", 'class': 'form-control'})
    )
    
    
    
class ForgotPasswordForm(forms.Form):  
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password", 'class': 'form-control'})
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", 'class': 'form-control'})
    )