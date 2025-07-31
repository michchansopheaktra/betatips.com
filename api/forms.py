# blog/forms.py

from django import forms
from .models import Post, Category, Profile
from taggit.forms import TagWidget
from ckeditor.widgets import CKEditorWidget 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'facebook', 'twitter', 'linkedin', 'instagram']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about yourself...',
                'rows': 6
            }),
            'facebook': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Facebook URL'
            }),
            'twitter': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Twitter URL'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'LinkedIn URL'
            }),
            'instagram': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Instagram URL'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap class to image input separately
        self.fields['profile_picture'].widget.attrs.update({
            'class': 'form-control'
        })

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'tags', 'image', 'author']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'content': CKEditorWidget(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tags': TagWidget(attrs={
                'class': 'form-control',
                'placeholder': 'Add tags separated by commas'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'author': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })