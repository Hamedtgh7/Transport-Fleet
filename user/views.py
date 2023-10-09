from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from .serializers import UserSerializer
from .models import User
import jwt

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title='user',
        default_version='v1',
    )
)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['POST'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        errors = []
        if username is '':
            errors.append('Usernamae required')
        if password is '':
            errors.append('Password required')

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username, password=password)
            if user.password == password:
                payload = {
                    'username': username
                }
                token = jwt.encode(
                    payload=payload, key='maypp', algorithm='HS256')
                return Response(token)
            else:
                return Response('invalid', status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response('User not found', status=status.HTTP_404_NOT_FOUND)


@api_view()
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')

    errors = []
    if username is None:
        errors.append('Username required')
    if password is None:
        errors.append('Password')

    if errors:
        return JsonResponse({
            'ok': False,
            'errors': errors
        }, status=400)

    User.objects.create(username=username, password=password)
