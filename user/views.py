from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.views import APIView
from rest_framework import status
from .serializers import LoginUserSerializer, RegisterUserSerializer, RegisterPhoneSerializer, CompanyCarSerializer, LocationSerializer, StandardSerializer
from .models import User, Company, Location, Car, Standard
from .tasks import create_cars
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


class CompanyCarView(CreateModelMixin, GenericViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanyCarSerializer

    def create(self, request, *args, **kwargs):
        serializer = CompanyCarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data['name']
        car_numbers = serializer.validated_data['car_numbers']
        user = get_object_or_404(
            User, username=serializer.validated_data['username'])

        company = Company.objects.create(name=name, user=user)

        create_cars.delay(company.id, car_numbers)

        return Response(status=status.HTTP_201_CREATED)


class StandardView(CreateModelMixin, GenericViewSet, DestroyModelMixin, UpdateModelMixin):
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer

    def perform_create(self, serializer):
        standard_instance = serializer.save()
        with redis.Redis('localhost', port=6379)as redis_cache:
            cache_key = f'standard_{standard_instance.name}'
            redis_cache.setex(cache_key, value=serializer.data)

    def perform_update(self, serializer):
        standard_instance = serializer.save()
        with redis.Redis('localhost', port=6379)as redis_cache:
            cache_key = f'standard_{standard_instance.name}'
            redis_cache.setex(cache_key, value=serializer.data)

    def perform_destroy(self, instance):
        with redis.Redis('localhost', port=6379)as redis_cache:
            redis_cache.delete(f'standard_{instance.name}')
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
        Location.objects.create(latitude=latitude, longitude=longitude,
                                acceleration=acceleration, speed=speed, car=car)
        return Response(status=status.HTTP_201_CREATED)
