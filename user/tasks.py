from celery import shared_task
from .models import Car, Company, WrongeCars
import json
import redis


@shared_task
def create_cars(company_id, car_numbers):
    company = Company.objects.get(id=company_id)
    for _ in range(car_numbers):
        Car.objects.create(company=company)


@shared_task
def wrong_cars(latitude, longitude, speed, acceleration, car_id, company_id, location_data):
    company = Company.objects.get(id=company_id)
    with redis.Redis(host='localhost', port=6379) as redis_cache:
        cache_key = f'standard_{company_id}'
        standard_data = json.loads(redis_cache.get(cache_key).decode('utf-8'))

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
            WrongeCars.objects.create(company=company, script=script)

        if longitude <= min_longitude or longitude >= max_longitude:
            script = f'car with id: {car_id} has latitude: {longitude} out of range.'
            WrongeCars.objects.create(company=company, script=script)

        if speed <= min_speed or speed >= max_speed:
            script = f'car with id: {car_id} has latitude: {speed} out of range.'
            WrongeCars.objects.create(company=company, script=script)

        if acceleration <= min_acceleration or acceleration >= max_acceleration:
            script = f'car with id: {car_id} has latitude: {acceleration} out of range.'
            WrongeCars.objects.create(company=company, script=script)

        pk = location_data['id']
        if script is '':
            cache_key = f'correct_location_{pk}'
            redis_cache.rpush(cache_key, value=json.dumps(location_data))
        else:
            cache_key = f'wrong_location_{pk}'
            redis_cache.rpush(cache_key, values=json.dumps(location_data))
