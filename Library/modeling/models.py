from django.contrib.auth.models import User as BaseUser
from django.db import models


class User(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)


class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ManyToManyField(Author, related_name='books')

    def __str__(self) -> str:
        return self.title
