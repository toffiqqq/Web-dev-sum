from django import forms
from .models import Movie, Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class  MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'year', 'genre', 'preview', 'video']

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']