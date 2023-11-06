from django.shortcuts import get_object_or_404
from django.core.validators import MinValueValidator
from rest_framework import serializers
from .models import User, Company, Location, Standard, Messages, Report
import re


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = get_object_or_404(User, username=username)

        if user.password != password:
            return serializers.ValidationError('Invalid password')

        return data


class RegisterUserSerializer(serializers.ModelSerializer):
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


class RegisterPhoneSerializer(serializers.ModelSerializer):

    def validate_phone(self, value):
        if (not value.startswith('0')) or (not value.isdigit()):
            raise serializers.ValidationError('Phone number is not valid.')
        return value

    class Meta:
        model = User
        fields = ['username', 'phone']


class CompanyCarSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    otp = serializers.CharField(max_length=6)
    car_numbers = serializers.IntegerField()
    name = serializers.CharField(max_length=255)

    def validate(self, data):
        name = data.get('name')
        car_numbers = data.get('car_numbers')

        if not re.match('[آ-ی]+$', name.replace(' ', '')):
            raise serializers.ValidationError('Name is not valid.')

        if car_numbers <= 0:
            raise serializers.ValidationError(
                'Number of cars should be positive.')

        return data

    class Meta:
        model = Company
        fields = ['username', 'otp', 'name', 'car_numbers']


class MessagesSerialiezer(serializers.ModelSerializer):
    script = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = Messages
        fields = ['script']


class StandardSerializer(serializers.ModelSerializer):

    def validate(self, data):
        min_speed = data.get('min_speed')
        max_speed = data.get('max_speed')
        if max_speed <= min_speed:
            raise serializers.ValidationError(
                'Maximum speed should be more than minimum speed.')

        min_latitude = data.get('min_latitude')
        max_latitude = data.get('max_latitude')
        if max_latitude <= min_latitude:
            raise serializers.ValidationError(
                'Maximum latitude should be more than minimum latitude.')

        min_longitude = data.get('min_longitude')
        max_longitude = data.get('max_longitude')
        if max_longitude <= min_longitude:
            raise serializers.ValidationError(
                'Maximum longitude should be more than minimum longitude.')

        min_acceleration = data.get('min_acceleration')
        max_acceleration = data.get('max_acceleration')
        if max_acceleration <= min_acceleration:
            raise serializers.ValidationError(
                'Maximum acceleration should be more than minimum acceleration.')

        return data

    def save(self, **kwargs):
        company = self.context['company_id']
        existing_standard = Standard.objects.filter(company=company).first()

        if existing_standard:
            for attr, value in self.validated_data.items():
                setattr(existing_standard, attr, value)
            existing_standard.save()
            return existing_standard
        else:
            self.instance = Standard.objects.create(
                company=company, **self.validated_data)
            return self.instance

    class Meta:
        model = Standard
        fields = ['min_speed', 'max_speed', 'min_latitude', 'max_latitude', 'min_longitude',
                  'max_longitude', 'min_acceleration', 'max_acceleration']


class LocationSerializer(serializers.ModelSerializer):
    car_id = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = Location
        fields = ['latitude', 'longitude', 'speed', 'car_id', 'acceleration']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['right_distance', 'car']
