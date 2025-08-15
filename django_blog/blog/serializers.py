from .models import Post
from rest_framework import serializers


#serialize models
class PostSerializer(serializers.ModelSerializer):
    model = Post
    fields = '__all__'

