from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User, Company
import re


class LoginUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class Register1UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, validators=[
                                     UniqueValidator(queryset=User.objects.all())])

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username.replace(' ', '').isalnum():
            raise serializers.ValidationError(
                'Username should only contains numbers, spaces and letters.')

        if not password.isalnum():
            raise serializers.ValidationError(
                'Password should only contains numbers and letters.')

        if len(password) < 6:
            raise serializers.ValidationError(
                'Password should have at least 6 characters.')

        return data

    class Meta:
        model = User
        fields = ['username', 'password']


class Register2UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=11, validators=[
        UniqueValidator(queryset=User.objects.all())])

    def validate_phone(self, value):
        if (not value.startswith('0')) or (not value.isdigit()):
            raise serializers.ValidationError('Phone number is not valid.')
        return value

    class Meta:
        model = User
        fields = ['phone']


class Register3UserSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6)

    def validate_name(self, value):
        if not re.match('[آ-ی]+$', value.replace(' ', '')):
            raise serializers.ValidationError('Name is not valid.')
        return value

    class Meta:
        model = Company
        fields = ['otp', 'name', 'number_cars']
