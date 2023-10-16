from django.conf import settings
from django.db import transaction
from asgiref.sync import sync_to_async
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from .serializers import LoginUserSerializer, Register1UserSerializer, Register2UserSerializer, Register3UserSerializer
from .models import User, Company
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


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'register1':
            return Register1UserSerializer
        elif self.action == 'register2':
            return Register2UserSerializer
        elif self.action == 'register3':
            return Register3UserSerializer
        elif self.action == 'login':
            return LoginUserSerializer

    @action(detail=False, methods=['POST'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
            if user.password == password:
                payload = {
                    'username': username
                }
                token = jwt.encode(
                    payload=payload, key=settings.JWT_KEY, algorithm='HS256')
                return Response(token)
            else:
                return Response('Invalid password', status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response('User not found', status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['POST'])
    def register1(self, request):
        serializer = Register1UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.session['username'] = serializer.validated_data['username']
        request.session['password'] = serializer.validated_data['password']

        redirect_url = '/user/register2/'
        return Response(status=status.HTTP_302_FOUND, headers={'Location': redirect_url})

    @action(detail=False, methods=['POST'])
    def register2(self, request):
        serializer = Register2UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        otp = str(generate_otp())

        request.session['opt'] = otp
        request.session['phone'] = phone

        redirect_url = '/user/register3'
        return Response(status=status.HTTP_302_FOUND, headers={'Location': redirect_url})

    @action(detail=False, methods=['POST'])
    async def register3(self, request):
        user_otp = request.data.get('opt')
        real_otp = request.session.get('otp')

        if user_otp == real_otp:
            serailizer = Register3UserSerializer(data=request.data)
            serailizer.is_valid(raise_exception=True)
            username = request.session.get('username')
            password = request.session.get('password')
            phone = request.session.get('phone')
            name = serailizer.validated_data['name']
            number_cars = serailizer.validated_data['number_cars']

            with transaction.atomic():
                user = await sync_to_async(User.objects.create)(username=username, password=password, phone=phone)
                company = await sync_to_async(Company.objects.create)(name=name, number_cars=number_cars, user=user)

            del request.session['username']
            del request.session['password']
            del request.session['otp']
            del request.session['phone']

            return Response('User and company Created', status=status.HTTP_201_CREATED)
        else:
            return Response('Invalid OTP', status=status.HTTP_403_FORBIDDEN)
