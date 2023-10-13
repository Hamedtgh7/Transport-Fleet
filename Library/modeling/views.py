from rest_framework.viewsets import ModelViewSet
from .serializers import UserSerialzier, AuthorSerializer, BookSerializer
from .models import User, Author, Book
from .permissions import IsAdminOrReadOnly


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerialzier
    permission_classes = [IsAdminOrReadOnly]


class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]


class AuthorBooksViewSet(ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        Book.objects.filter(author_id=self.kwargs['author_pk'])
