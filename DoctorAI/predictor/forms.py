from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, GenomeUpload

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    middle_name = forms.CharField(max_length=30, required=False)
    date_of_birth = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    mobile_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'middle_name', 'date_of_birth', 'mobile_number', 'password1', 'password2')


class GenomeForm(forms.ModelForm):
    class Meta:
        model = GenomeUpload
        fields = ['genome_file']