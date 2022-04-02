import time
import os

import tweepy
from redis import Redis

from MessageBuilders import RandomAnimalMessageBuilder


def get_redis(redis_url):
    instance = Redis.from_url(redis_url, ssl_cert_reqs=False)

    if not instance.ping():
        raise ConnectionError('Redis instance is down.')

    return instance


def get_twitter(api_key, api_secret_key, access_key, access_secret):
    auth = tweepy.OAuthHandler(api_key, api_secret_key, access_key, access_secret)

    return tweepy.API(auth, wait_on_rate_limit=True)

def get_animals():
    with open('animals.txt', 'r', encoding="utf8") as file:
        return list(map(lambda animal: animal.split('(')[0].strip(), file.readlines()))


def _main_():
    r = get_redis(os.environ['REDIS_URL'])
    api = get_twitter(os.environ['API_KEY'], os.environ['API_SECRET_KEY'], os.environ['ACCESS_KEY'], os.environ['ACCESS_SECRET'])

    animals = get_animals()
    RandomAnimalMessageBuilder.add_animals(animals)

    last_seen_tweet_id = str(r.get('last_seen_tweet_id'))
    tweets = api.mentions_timeline(since_id=last_seen_tweet_id)

    print('deu bao')
    print('Ultimo ID pesquisado:' + last_seen_tweet_id)

    for tweet in reversed(tweets):
        random_animal_message = RandomAnimalMessageBuilder.build_random_animal_message()
        r.set('last_seen_tweet_id', tweet.id)
        api.update_status(f"@{tweet.user.screen_name} {random_animal_message}", in_reply_to_status_id=tweet.id)


while True:
    _main_()
    time.sleep(60)
