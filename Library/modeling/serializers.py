from rest_framework import serializers
from .models import User, Author, Book


class UserSerialzier(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = '__all__'
