from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework.views import APIView
from rest_framework import status
from datetime import timedelta
from .serializers import LoginUserSerializer, RegisterUserSerializer, RegisterPhoneSerializer, CompanyCarSerializer, LocationSerializer, StandardSerializer, MessagesSerialiezer, ReportSerializer
from .models import User, Company, Location, Car, Standard, Messages, Report
from .permissions import Permissions
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
    queryset = Company.objects.all()
    serializer_class = CompanyCarSerializer

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

        return Response({'message': 'Company and Cars created'}, status=status.HTTP_201_CREATED)


class MessagesView(ListModelMixin, GenericViewSet):
    serializer_class = MessagesSerialiezer

    def get_queryset(self):
        username = self.request.allow
        return Messages.objects.filter(company=username.company)


class StandardView(CreateModelMixin, GenericViewSet, DestroyModelMixin, UpdateModelMixin):
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer
    permission_classes = [Permissions]

    def get_serializer_context(self):
        username = self.request.allow
        company = User.objects.get(username=username).company
        return {'company_id': company}

    def get_object(self):
        username = self.request.allow
        return User.objects.get(username=username).company.standard

    def perform_create(self, serializer):
        serializer.save()
        username = self.request.allow
        company_id = User.objects.get(username=username).company.pk
        with redis.Redis('localhost', port=6379)as redis_cache:
            cache_key = f'standard_{company_id}'
            json_serializer = json.dumps(serializer.data)
            redis_cache.set(cache_key, value=json_serializer)

    def perform_update(self, serializer):
        serializer.save()
        username = self.request.allow
        company_id = User.objects.get(username=username).company.pk
        with redis.Redis('localhost', port=6379)as redis_cache:
            cache_key = f'standard_{company_id}'
            json_serializer = json.dumps(serializer.data)
            redis_cache.set(cache_key, value=json_serializer)

    def perform_destroy(self, instance):
        username = self.request.allow
        company_id = User.objects.get(username=username).company.pk
        with redis.Redis('localhost', port=6379)as redis_cache:
            redis_cache.delete(f'standard_{company_id}')
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
        wrong_cars.delay(latitude, longitude, speed,
                         acceleration, car_id, car.company.id)

        return Response({'message': 'Location created.'}, status=status.HTTP_201_CREATED)


class ReportView(ListModelMixin, GenericViewSet):
    serializer_class = ReportSerializer

    def get_daily_reports(self):
        username = self.request.allow
        company = User.objects.get(username=username).company
        start_time = timezone.now()-timedelta(days=1)
        return Report.objects.filter(company=company, created_at__range=[start_time, timezone.now()])

    def get_weekly_reports(self):
        username = self.request.allow
        company = User.objects.get(username=username).company
        start_time = timezone.now()-timedelta(weeks=1)
        return Report.objects.filter(company=company, created_at__range=[start_time, timezone.now()])

    def get_monthly_reports(self):
        username = self.request.allow
        company = User.objects.get(username=username).company
        start_time = timezone.now()-timedelta(days=30)
        return Report.objects.filter(company=company, created_at__range=[start_time, timezone.now()])
