from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Post, Comment
from taggit.forms import TagWidget
import re
from django.utils.html import strip_tags

# Form to create User and edit.
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


# Form for creating new blog posts
class PostCreationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'tags']  # include content here

        widgets = {
            # 'tags': forms.TextInput(attrs={'placeholder': 'Add tags separated by commas'}),
            'tags': TagWidget(),
        }

    def clean_title(self):
        """
        Custom validation for title field
        """
        title = self.cleaned_data.get('title')
        
        if not title:
            raise ValidationError("Title is required.")
        
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        # Check minimum length
        if len(title) < 5:
            raise ValidationError("Title must be at least 5 characters long.")
        
        # Check if title is too generic
        generic_titles = [
            'untitled', 'new post', 'blog post', 'my post', 
            'test', 'hello world', 'sample'
        ]
        if title.lower() in generic_titles:
            raise ValidationError("Please choose a more descriptive title.")
        
        return title
    
    def clean_content(self):
        """Custom validation for content field."""

        content = self.cleaned_data.get('content')

        # Strip HTML tags for length validation
        plain_content = strip_tags(content).strip()

        #watch for max character input in content
        if len(content) > 5000:
            raise ValidationError("Content is too long")

        # Check for spam-like content (repeated characters)
        if re.search(r'(.)\1{10,}', plain_content):
            raise ValidationError("Content appears to contain spam-like repeated characters.")

        return content
    
    # Comment form and validation
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a comment...'}),
        }

    def clean_commnent(self):
        '''custome validation for comment field'''

        content = self.cleaned_data.get('content')

        if len(content) > 2000:
            raise ValidationError('Your comment is too long')
        