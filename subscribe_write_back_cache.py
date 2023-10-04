from redis import Redis
import json

redis = Redis(host='localhost', port=6379, decode_responses=True)

pubsub = redis.pubsub()
pubsub.subscribe('channel')

cache = {}
for message in pubsub.listen():
    data = json.loads(message)
    cache[data['id']] = data
