from django.db import models
from django.forms import model_to_dict
from redis import Redis
import json


redis = Redis(host='localhost', port=6379, decode_responses=True)


class TheModel(models.Model):
    title = models.CharField(max_length=255)

    @classmethod
    def get_cache(cls, id):
        cache_key = f'model_{id}'

        if redis.get(cache_key) is None:
            object = cls.objects.get(id=id)
            redis.set(cache_key, json.dumps(model_to_dict(object)))
            return object

        return TheModel(**json.loads(redis.get(cache_key)))

    def save(self, *args, **kwargs):
        super(TheModel, self).save(*args, **kwargs)
        cache_key = f'model_{self.id}'
        redis.set(cache_key, json.dumps(model_to_dict(self)))

    def delete(self, *args, **kwargs):
        super(TheModel, self).delete(*args, **kwargs)
        cache_key = f'model_{self.id}'
        redis.delete(cache_key)
