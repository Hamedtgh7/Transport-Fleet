from celery import shared_task
from .models import Car, Company


@shared_task
def create_cars(company_id, car_numbers):
    company = Company.objects.get(id=company_id)
    for _ in range(car_numbers):
        Car.objects.create(company=company)
