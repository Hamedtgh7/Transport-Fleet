from rest_framework.response import Response
import jwt


class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'myapp/user/login' or 'admin/' in request.path:
            return self.get_response(request)

        token = request.headers.get('Authorization')
        try:
            jwt.decode(
                jwt=token,
                algorithms='HS256',
                key='myapp'
            )
        except jwt.DecodeError:
            return Response('invalid')

        response = self.get_response(request)
        return response
