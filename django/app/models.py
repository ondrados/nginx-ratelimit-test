import requests
import time
from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import get_random_string

from contextlib import contextmanager


class TestModel(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    @property
    def oauth_access_token_header(self):
        return {
            "Oauth-Token": "test"
        }

    def obtain_api_access_token(self):
        res = requests.post(
            "http://172.19.0.1:80/token",
            headers=self.oauth_access_token_header
        )
        return res.json()

    @property
    def api_access_token_header(self):
        return {
            "Access-Token": self.get_api_token()[1]
        }

    def set_new_api_token(self):
        data = self.obtain_api_access_token()
        token = data.get("access_token")
        timeout = data.get("expires_in")

        key = f"{self.id}_api_token_{get_random_string(6)}"
        cache.set(key, (token, 0), timeout=timeout - 1)

        return key, token, 0

    def clear_api_tokens(self):
        keys = cache.keys(f"{self.id}_api_token_*")
        return cache.delete_many(keys)

    def get_api_token(self):
        with cache.lock(key=f"{self.id}_lock"):
            keys = cache.keys(f"{self.id}_api_token_*")

            if not keys:
                key, token, count = self.set_new_api_token()
                new_count = self.increase_token_count(key, token, count)
                return key, token, new_count
            else:
                for key, (token, count) in cache.get_many(keys).items():
                    if count < 3:
                        new_count = self.increase_token_count(key, token, count)
                        return key, token, new_count
                if len(keys) < 5:
                    key, token, count = self.set_new_api_token()
                    new_count = self.increase_token_count(key, token, count)
                    return key, token, new_count
        return None, None, None

    @classmethod
    def increase_token_count(cls, key, token, count):
        count += 1
        cache.set(key, (token, count), cache.ttl(key))
        return count

    @classmethod
    def decrease_token_count(cls, key: str, token: str, count: int) -> int:
        count -= 1
        cache.set(key, (token, count), cache.ttl(key))
        return count

    @contextmanager
    def api_token_manager(self, timeout=5.0, *args, **kwargs):
        """
        Context manager to ensure maximum ratelimiting per token.
        3 concurrent requests per 1 of 5 valid tokens = 15 requests at a time
        """
        token = None
        time_to_wait = time.time() + timeout
        while time.time() < time_to_wait:
            key, token, count = self.get_api_token(*args, **kwargs)
            if token:
                break
            # waiting for available token
            time.sleep(0.1)
        try:
            yield token
        finally:
            if token:
                with cache.lock(key=f"{self.id}_lock"):
                    (token, count) = cache.get(key)
                    self.decrease_token_count(key, token, count)

    def make_api_request(self, method, url, **kwargs):
        with self.api_token_manager() as token:
            res = requests.request(method, url, headers={
                "Access-Token": token
            }, **kwargs)

            res.raise_for_status()
            return res

    def get_data(self):
        res = self.make_api_request("get", "http://172.19.0.1:80")

        try:
            res_json = res.json()
            return res_json
        except:
            return res.status_code


    ##################### OLD ######################
    def get_api_token_old(self):
        keys = cache.keys(f"{self.id}_api_token_*")

        if not keys:
            _, token, _ = self.set_new_api_token()
        else:
            token, _ = cache.get(keys[0])

        return token

    @contextmanager
    def api_token_old(self, *args, **kwargs):
        token = self.get_api_token_old(*args, **kwargs)
        try:
            yield token
        finally:
            pass
