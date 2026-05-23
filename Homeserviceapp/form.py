from django.contrib.auth.forms import UserCreationForm
from django import forms

from Homeserviceapp.models import Login, UserRegistration, Category, WorkerRegistration, Availability, Feedback


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class LoginForm(UserCreationForm):
    username = forms.CharField()
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='confirm password', widget=forms.PasswordInput)

    class Meta:
        model = Login
        fields = ('username', 'password1', 'password2')


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = UserRegistration
        fields = ('name', 'address', 'contact')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class WorkerRegistrationForm(forms.ModelForm):
    class Meta:
        model = WorkerRegistration
        fields = ('name', 'category', 'address', 'contact', 'experience', 'image','paypal_email')


class AvailabilityForm(forms.ModelForm):
    date = forms.DateField(widget=DateInput)
    time = forms.TimeField(widget=TimeInput)

    class Meta:
        model = Availability
        fields = ('date', 'time')


class FeedbackForm(forms.ModelForm):
    date = forms.DateField(widget=DateInput)

    class Meta:
        model=Feedback
        fields=('date','name','complaint')
