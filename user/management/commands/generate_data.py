from django.core.management.base import BaseCommand
from user.models import Company, User, Car, Standard, Messages, Location
from typing import Any
import random
import math


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:

        user = User.objects.get(id=1)
        companies = []
        for i in range(5):
            company = Company.objects.create(name=f'company_{i}', user=user)
            companies.append(company)

        for company in companies:
            Car.objects.create(company=company)

        for company in companies:
            min_speed = random.uniform(0, 100),
            max_speed = random.uniform(min_speed, 200)
            min_latitude = random.uniform(-500, 100)
            max_latitude = random.uniform(min_latitude, 500)
            min_longitude = random.uniform(-500, 100)
            max_longitude = random.uniform(min_longitude, 500)
            min_acceleration = random.uniform(0, 5)
            max_acceleration = random.uniform(min_acceleration, 10)

            Standard.objects.create(
                min_speed=min_speed,
                max_speed=max_speed,
                min_latitude=min_latitude,
                max_latitude=max_latitude,
                min_longitude=min_longitude,
                max_longitude=max_longitude,
                min_acceleration=min_acceleration,
                max_acceleration=max_acceleration,
                company=company
            )

        for company in companies:
            Messages.objects.create(
                script='sample script',
                company=company
            )

        for car in Car.objects.all():
            latitude = random.uniform(-500, 500)
            longitude = random.uniform(-500, 500)
            speed = random.uniform(1, 100)
            acceleration = random.uniform(1, 10)
            for i in range(10):
                Location.objects.create(
                    latitude=latitude,
                    longitude=longitude,
                    speed=speed,
                    acceleration=acceleration,
                    car=car
                )
                acceleration = random.uniform(1, 10)
                speed = random.uniform(1, 100)
                time = 2
                delta_latitude = (speed*time)/(60*1852)
                delta_longitude = (speed*time) / \
                    (60*1852*math.cos(math.radians(latitude)))
                latitude += delta_latitude
                longitude += delta_longitude
