from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import jwt


class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        token = request.META.get('HTTP_Authorization')
        if token:
            try:
                decoded_token = jwt.decode(
                    jwt=token,
                    algorithms=['HS256'],
                    key=settings.JWT_KEY
                )
                username = decoded_token.get('username')
                if username:
                    request.allow = username
                else:
                    request.allow = None
            except jwt.DecodeError:
                return Response('Invalid token', status=status.HTTP_401_UNAUTHORIZED)
        else:
            Response('Invalid header', status=status.HTTP_401_UNAUTHORIZED)

        response = self.get_response(request)
        return response
