from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from redis import Redis
import json

redis = Redis(host='localhost', port=6379, decode_responses=True)


class TheModel(models.Model):
    title = models.CharField(max_length=255)


@receiver(post_delete, sender=TheModel)
@receiver(post_save, sender=TheModel)
def redis_cache(sender, instance, **kwargs):
    data = {'id': instance.id}
    redis.publish(channel='channel', message=json.dumps(data))
