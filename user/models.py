from django.db import models


class User(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=11)

    def __str__(self) -> str:
        return self.username


class Company(models.Model):
    name = models.CharField(max_length=255)
    number_cars = models.PositiveIntegerField()
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='user', null=True, blank=True)

    def __str__(self) -> str:
        return self.name
