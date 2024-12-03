from django.shortcuts import get_object_or_404
from celery import shared_task
from datetime import datetime, timedelta
from .models import Car, Company, Messages, Location, Report
import json
import redis
import math
import re


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

                # right speed
                if speed <= min_speed or speed >= max_speed:
                    report_cache_key = f'wrong_speed_distance_{car_id}'
                    time_key = f'wrong_speed_time_{car_id}'
                    wrong_value_cache = redis_cache.get(report_cache_key)

                    if wrong_value_cache:
                        time_value_cache = float(
                            redis_cache.get(time_key).decode('utf-8'))
                        wrong_value_cache = float(
                            wrong_value_cache.decode('utf-8'))
                        wrong_value_cache += distance
                        time_value_cache += difference_time
                        redis_cache.set(report_cache_key,
                                        value=wrong_value_cache)
                        redis_cache.set(time_key, value=time_value_cache)

                    else:
                        redis_cache.set(report_cache_key, value=distance)
                        redis_cache.set(time_key, value=difference_time)

                else:
                    report_cache_key = f'right_speed_distance_{car_id}'
                    time_key = f'right_speed_time_{car_id}'
                    right_value_cache = redis_cache.get(report_cache_key)

                    if right_value_cache:
                        time_value_cache = float(
                            redis_cache.get(time_key).decode('utf-8'))
                        right_value_cache = float(
                            right_value_cache.decode('utf-8'))
                        time_value_cache += difference_time
                        right_value_cache += distance
                        redis_cache.set(report_cache_key,
                                        value=right_value_cache)
                        redis_cache.set(time_key, value=time_value_cache)

                    else:
                        redis_cache.set(report_cache_key, value=distance)
                        redis_cache.set(time_key, value=difference_time)
                    #########

                # right acceleration
                if acceleration <= min_acceleration or acceleration >= max_acceleration:
                    report_cache_key = f'wrong_acceleration_distance_{car_id}'
                    time_key = f'wrong_acceleration_time_{car_id}'
                    wrong_value_cache = redis_cache.get(report_cache_key)

                    if wrong_value_cache:
                        wrong_value_cache = float(
                            wrong_value_cache.decode('utf-8'))
                        time_value_cache = float(
                            redis_cache.get(time_key).decode('utf-8'))
                        wrong_value_cache += distance
                        time_value_cache += difference_time
                        redis_cache.set(report_cache_key,
                                        value=wrong_value_cache)
                        redis_cache.set(time_key, value=time_value_cache)

                    else:
                        redis_cache.set(report_cache_key, value=distance)
                        redis_cache.set(time_key, value=difference_time)

                else:
                    report_cache_key = f'right_acceleration_distance_{car_id}'
                    time_key = f'right_acceleration_time_{car_id}'
                    right_value_cache = redis_cache.get(report_cache_key)

                    if right_value_cache:
                        right_value_cache = float(
                            right_value_cache.decode('utf-8'))
                        time_value_cache = float(
                            redis_cache.get(time_key).decode('utf-8'))
                        right_value_cache += distance
                        time_value_cache += difference_time
                        redis_cache.set(report_cache_key,
                                        value=right_value_cache)
                        redis_cache.set(time_key, value=time_value_cache)

                    else:
                        redis_cache.set(report_cache_key, value=distance)
                        redis_cache.set(time_key, value=difference_time)
                ###########
                if latitude <= min_latitude or latitude >= max_latitude or longitude <= min_longitude or longitude >= max_longitude:
                    report_cache_key = f'wrong_location_distance_{car_id}'
                    time_key = f'wrong_location_time_{car_id}'
                    wrong_value_cache = redis_cache.get(report_cache_key)

                    if wrong_value_cache:
                        wrong_value_cache = float(
                            wrong_value_cache.decode('utf-8'))
                        time_value_cache = float(
                            redis_cache.get(time_key).decode('utf-8'))
                        wrong_value_cache += distance
                        time_value_cache += difference_time
                        redis_cache.set(report_cache_key,
                                        value=wrong_value_cache)
                        redis_cache.set(time_key, value=time_value_cache)

                    else:
                        redis_cache.set(report_cache_key, value=distance)
                        redis_cache.set(time_key, value=difference_time)

                else:
                    report_cache_key = f'right_location_distance_{car_id}'
                    time_key = f'right_location_time_{car_id}'
                    right_value_cache = redis_cache.get(report_cache_key)

                    if right_value_cache:
                        right_value_cache = float(
                            right_value_cache.decode('utf-8'))
                        time_value_cache = float(
                            redis_cache.get(time_key).decode('utf-8'))
                        right_value_cache += distance
                        time_value_cache += difference_time
                        redis_cache.set(report_cache_key,
                                        value=right_value_cache)
                        redis_cache.set(time_key, value=time_value_cache)

                    else:
                        redis_cache.set(report_cache_key, value=distance)
                        redis_cache.set(time_key, value=difference_time)

            else:
                start_time = redis_cache.get(f'start_time_{car_id}')
                exist_peroid = redis_cache.get(f'period_time_{car_id}')
                if exist_peroid:
                    exist_peroid += f'{start_time}-{final_time}\n'
                    redis_cache.set(
                        f'period_time_{car_id}', value=exist_peroid)
                else:
                    final_time = exist_cache['created_time']
                    redis_cache.set(
                        f'period_time_{car_id}', value=f'{start_time}-{final_time}\n')

            redis_cache.set(exist_cache_key,
                            value=json.dumps(location_data))

        else:
            redis_cache.set(f'start_time_{car_id}',
                            value=location_data['created_time'])
            redis_cache.set(exist_cache_key, value=json.dumps(location_data))


@shared_task
def report():
    with redis.Redis(host='localhost', port=6379) as redis_cache:
        keys = redis_cache.keys('right_speed_distance_*')

        for key in keys:
            right_speed_distance = float(redis_cache.get(key).decode('utf-8'))
            wrong_speed_distance = float(redis_cache.get(key).decode('utf-8'))
            car_id = int(re.search(r'right_speed_distance_(\d+)',
                         key.decode('utf-8')).group(1))
            value_cache = redis_cache.get(
                f'right_acceleration_distance_{car_id}')
            right_acceleration_distance = float(value_cache.decode(
                'utf-8')) if value_cache is not None else 0.0
            value_cache = redis_cache.get(
                f'wrong_location_distance_{car_id}')
            wrong_location_distance = float(value_cache.decode(
                'utf-8')) if value_cache is not None else 0.0
            value_cache = redis_cache.get(
                f'right_speed_time_{car_id}')
            speed_time = float(value_cache.decode('utf-8')
                               ) if value_cache is not None else 0.0
            value_cache = redis_cache.get(
                f'right_acceleration_time_{car_id}')
            acceleration_time = float(value_cache.decode(
                'utf-8')) if value_cache is not None else 0.0
            value_cache = redis_cache.get(
                f'wrong_location_time_{car_id}')
            location_time = float(value_cache.decode(
                'utf-8')) if value_cache is not None else 0.0
            value_cache = redis_cache.get(f'period_time_{car_id}')
            period_times = value_cache.decode(
                'utf-8') if value_cache is not None else ''

            # speed_hour, remainder = divmod(speed_time, 3600)
            # speed_minute, speed_second = divmod(remainder, 60)
            # right_speed_time = f"{int(speed_hour):04}:{int(speed_minute):02}:{int(speed_second):02}"

            right_speed_time = str(timedelta(seconds=speed_time))

            # acceleration_hour, remainder = divmod(acceleration_time, 3600)
            # acceleration_minute, acceleration_second = divmod(remainder, 60)
            # right_acceleration_time = f"{int(acceleration_hour):04}:{int(acceleration_minute):02}:{int(acceleration_second):02}"

            right_acceleration_time = str(timedelta(seconds=acceleration_time))

            # location_hour, remainder = divmod(location_time, 3600)
            # location_minute, location_second = divmod(location_hour, 60)
            # wrong_location_time = f"{int(location_hour):04}:{int(location_minute):02}:{int(location_second):02}"

            wrong_location_time = str(timedelta(seconds=location_time))

            total_distance = right_speed_distance+wrong_speed_distance

            car = Car.objects.get(id=car_id)
            company = car.company
            Report.objects.create(right_acceleration_time=right_acceleration_time, right_speed_time=right_speed_time, right_speed_distance=right_speed_distance, right_acceleration_distance=right_acceleration_distance,
                                  period_times=period_times, total_distance=total_distance, wrong_location_time=wrong_location_time, wrong_location_distance=wrong_location_distance, company=company, car=car)
            redis_cache.set(key, 0)
            redis_cache.set(f'wrong_speed_distance_{car_id}', 0)
            redis_cache.set(f'right_acceleration_distance_{car_id}', 0)
            redis_cache.set(f'wrong_acceleration_distance_{car_id}', 0)
            redis_cache.set(f'right_location_distance_{car_id}', 0)
            redis_cache.set(f'wrong_location_distance_{car_id}', 0)
            redis_cache.set(f'right_speed_time_{car_id}', 0)
            redis_cache.set(f'wrong_speed_time_{car_id}', 0)
            redis_cache.set(f'right_acceleration_time_{car_id}', 0)
            redis_cache.set(f'wrong_acceleration_time_{car_id}', 0)
            redis_cache.set(f'wrong_location_time_{car_id}', 0)
            redis_cache.set(f'right_location_time_{car_id}', 0)
            redis_cache.set(f'period_time_{car_id}', 0)
