from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.views import APIView
from rest_framework import status
from .serializers import LoginUserSerializer, RegisterUserSerializer, RegisterPhoneSerializer, CompanyCarSerializer, LocationSerializer, StandardSerializer, WrongCarSerialiezer
from .models import User, Company, Location, Car, Standard, WrongeCars
from .tasks import create_cars, wrong_cars
import json
import redis
import jwt
import random

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title='user',
        default_version='v1',
    )
)


def generate_otp():
    return random.randint(100000, 999999)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']

        payload = {
            'username': username
        }
        token = jwt.encode(
            payload=payload, key=settings.JWT_KEY, algorithm='HS256')
        return Response(token)


class RegisterUserView(CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer


class RegisterPhoneView(UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterPhoneSerializer

    def update(self, request, *args, **kwargs):
        otp = str(generate_otp())
        username = request.data.get('username')
        phone = request.data.get('phone')

        with redis.Redis(host='localhost', port=6379) as redis_cache:
            cache_key = f'otp_{username}'
            redis_cache.setex(cache_key, time=120, value=otp)

        user = get_object_or_404(User, username=username)
        user.phone = phone
        user.save()

        return Response(otp)


class CompanyCarView(CreateModelMixin, GenericViewSet, RetrieveModelMixin):
    def get_queryset(self):
        if self.action == 'create':
            return Company.objects.all()
        elif self.action == 'retrieve':
            return WrongeCars.objects.filter(company_id=self.kwargs['pk'])
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == 'create':
            return CompanyCarSerializer
        elif self.action == 'retrieve':
            return WrongCarSerialiezer

    def create(self, request, *args, **kwargs):
        serializer = CompanyCarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        otp = serializer.validated_data['otp']

        user = get_object_or_404(User, username=username)
        cache_key = f'otp_{user.username}'
        with redis.Redis(host='localhost', port=6379) as redis_cache:
            stored_otp = redis_cache.get(cache_key).decode('utf-8')

        if not stored_otp:
            raise ValidationError('Otp expired')

        if otp != stored_otp:
            raise ValidationError('Invalid otp')

        name = serializer.validated_data['name']
        car_numbers = serializer.validated_data['car_numbers']

        company = Company.objects.create(name=name, user=user)

        create_cars.delay(company.id, car_numbers)

        return Response(status=status.HTTP_201_CREATED)


class StandardView(CreateModelMixin, GenericViewSet, DestroyModelMixin, UpdateModelMixin):
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer

    def perform_create(self, serializer):
        standard_instance = serializer.save()
        with redis.Redis('localhost', port=6379)as redis_cache:
            cache_key = f'standard_{standard_instance.company.id}'
            json_serializer = json.dumps(serializer.data)
            redis_cache.set(cache_key, value=json_serializer)

    def perform_update(self, serializer):
        standard_instance = serializer.save()
        with redis.Redis('localhost', port=6379)as redis_cache:
            cache_key = f'standard_{standard_instance.company.id}'
            print(cache_key)
            json_serializer = json.dumps(serializer.data)
            redis_cache.set(cache_key, value=json_serializer)

    def perform_destroy(self, instance):
        with redis.Redis('localhost', port=6379)as redis_cache:
            redis_cache.delete(f'standard_{instance.company.id}')
        return super().perform_destroy(instance)


class LocationView(CreateModelMixin, GenericViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        serializer = LocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        car_id = serializer.validated_data['car_id']
        latitude = serializer.validated_data['latitude']
        longitude = serializer.validated_data['longitude']
        acceleration = serializer.validated_data['acceleration']
        speed = serializer.validated_data['speed']
        car = get_object_or_404(Car, id=car_id)

        location = Location.objects.create(latitude=latitude, longitude=longitude,
                                           acceleration=acceleration, speed=speed, car=car)

        location_data = {
            'id': location.pk,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'acceleration': location.acceleration,
            'speed': location.speed,
            'created_time': location.created_at.isoformat(),
            'car_id': car_id,
        }

        wrong_cars.delay(latitude, longitude, speed,
                         acceleration, car_id, car.company.id, location_data)

        return Response(status=status.HTTP_201_CREATED)
