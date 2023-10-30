from django.core.validators import MinValueValidator
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=11, blank=True, unique=True)

    def __str__(self) -> str:
        return self.username


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='company')

    def __str__(self) -> str:
        return self.name


class Car(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)


class WrongeCars(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='out_of_range')
    script = models.CharField(max_length=255)


class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    speed = models.FloatField(validators=[MinValueValidator(0)])
    acceleration = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE, related_name='location')


class Standard(models.Model):
    min_speed = models.FloatField(validators=[MinValueValidator(0)])
    max_speed = models.FloatField(validators=[MinValueValidator(0)])
    min_latitude = models.FloatField()
    max_latitude = models.FloatField()
    min_longitude = models.FloatField()
    max_longitude = models.FloatField()
    min_acceleration = models.FloatField()
    max_acceleration = models.FloatField()
    company = models.OneToOneField(
        Company, on_delete=models.CASCADE, related_name='location')
