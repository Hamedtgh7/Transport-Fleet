from django.shortcuts import get_object_or_404
from celery import shared_task
from datetime import datetime
from .models import Car, Company, Messages, Location, Report
import json
import redis
import math
import re
import pdb


@shared_task
def create_cars(company_id, car_numbers):
    company = Company.objects.get(id=company_id)
    for _ in range(car_numbers):
        Car.objects.create(company=company)


@shared_task
def wrong_cars(latitude, longitude, speed, acceleration, car_id, company_id):

    car = get_object_or_404(Car, id=car_id)
    location = Location.objects.create(latitude=latitude, longitude=longitude,
                                       acceleration=acceleration, speed=speed, car=car)

    company = Company.objects.get(id=company_id)
    with redis.Redis(host='localhost', port=6379) as redis_cache:
        cache_key = f'standard_{company_id}'
        standard_data = json.loads(redis_cache.get(cache_key))

        min_latitude = standard_data['min_latitude']
        max_latitude = standard_data['max_latitude']
        min_longitude = standard_data['min_longitude']
        max_longitude = standard_data['max_longitude']
        min_acceleration = standard_data['min_acceleration']
        max_acceleration = standard_data['max_acceleration']
        min_speed = standard_data['min_speed']
        max_speed = standard_data['max_speed']
        script = ''
        if latitude <= min_latitude or latitude >= max_latitude:
            script = f'car with id: {car_id} has latitude: {latitude} out of range.'
            Messages.objects.create(company=company, script=script)

        if longitude <= min_longitude or longitude >= max_longitude:
            script = f'car with id: {car_id} has latitude: {longitude} out of range.'
            Messages.objects.create(company=company, script=script)

        if speed <= min_speed or speed >= max_speed:
            script = f'car with id: {car_id} has latitude: {speed} out of range.'
            Messages.objects.create(company=company, script=script)

        if acceleration <= min_acceleration or acceleration >= max_acceleration:
            script = f'car with id: {car_id} has latitude: {acceleration} out of range.'
            Messages.objects.create(company=company, script=script)

        location_data = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'acceleration': location.acceleration,
            'speed': location.speed,
            'created_time': location.created_at.isoformat(),
        }

        exist_cache_key = f'last_location_{car_id}'
        exist_cache = redis_cache.get(exist_cache_key)
        if exist_cache:
            exist_cache = json.loads(exist_cache)
            difference_time = (datetime.fromisoformat(
                location_data['created_time'])-datetime.fromisoformat(exist_cache['created_time'])).total_seconds()

            if difference_time < 10:
                distance = math.sqrt((location_data['latitude']-exist_cache['latitude'])**2+(
                    location_data['longitude']-exist_cache['longitude'])**2)
                if speed <= min_speed or speed >= max_speed:
                    report_cache_key = f'wrong_distance_{car_id}'
                    wrong_value_cache = redis_cache.get(report_cache_key)

                    if wrong_value_cache:
                        wrong_value_cache = float(
                            wrong_value_cache.decode('utf-8'))
                        wrong_value_cache += distance
                        redis_cache.set(report_cache_key,
                                        value=wrong_value_cache)

                    else:
                        redis_cache.set(report_cache_key, value=distance)

                else:
                    report_cache_key = f'right_distance_{car_id}'
                    right_value_cache = redis_cache.get(report_cache_key)

                    if right_value_cache:
                        right_value_cache = float(
                            right_value_cache.decode('utf-8'))
                        right_value_cache += distance
                        redis_cache.set(report_cache_key,
                                        value=right_value_cache)

                    else:
                        redis_cache.set(report_cache_key, value=distance)

            else:
                redis_cache.set(exist_cache_key,
                                value=json.dumps(location_data))

        else:
            redis_cache.set(exist_cache_key, value=json.dumps(location_data))


@shared_task
def report():
    with redis.Redis(host='localhost', port=6379) as redis_cache:
        keys = redis_cache.keys('right_distance_*')

        for key in keys:
            data = float(redis_cache.get(key).decode('utf-8'))
            car_id = int(re.search(r'right_distance_(\d+)',
                         key.decode('utf-8')).group(1))
            print(car_id)
            car = Car.objects.get(id=car_id)
            company = car.company
            Report.objects.create(right_distance=data,
                                  company=company, car=car)
