# blog/forms.py

from django import forms
from .models import Post, Category, Profile, AffiliateLink, Service
from taggit.forms import TagWidget
from ckeditor.widgets import CKEditorWidget 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import ZipUpload

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
        fields = ['title', 'content', 'category', 'tags', 'image', 'author', 'image_1', 'image_2', 'download', 'ads_1', 'ads_2', 'ads_3', 'ads_4', 'ads_5']
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
                'class': 'form-control', 'width=100%'
                'placeholder': 'Add tags separated by commas'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'author': forms.Select(attrs={
                'class': 'form-control'
            }),
            'download': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'ads_1': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'ads_2': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'ads_3': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'ads_4': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'ads_5': forms.TextInput(attrs={
                'class': 'form-control',
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

    # forms.py

class ZipUploadForm(forms.ModelForm):
    class Meta:
        model = ZipUpload
        fields = ['zip_file']


class AffiliateLinkForm(forms.ModelForm):
    class Meta:
        model = AffiliateLink
        fields = ['title', 'image', 'url']
        widgets = {
                    'title': forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'Enter post title'
                    }),
                    'image': forms.ClearableFileInput(attrs={
                        'class': 'form-control'
                    }),
                    'url': forms.TextInput(attrs={
                        'class': 'form-control',
                    }),
                }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'link']
        widgets = {
                    'title': forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': 'Enter post title'
                    }),

                    'description': forms.Textarea(attrs={
                        'class': 'form-control'
                    }),
                    'link': forms.TextInput(attrs={
                        'class': 'form-control',
                    }),
                }