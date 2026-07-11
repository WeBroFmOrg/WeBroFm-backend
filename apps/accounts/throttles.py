from django.core.cache import cache


class OTPRateThrottle:
    """
    Cache-based rate limiter: 3 OTP attempts per phone number per hour.
    Resets automatically after 1 hour of no activity.
    """

    CACHE_PREFIX = "otp_throttle_"
    MAX_ATTEMPTS = 3
    WINDOW_SECONDS = 3600  # 1 hour

    @classmethod
    def _key(cls, phone_number: str) -> str:
        return f"{cls.CACHE_PREFIX}{phone_number}"

    @classmethod
    def is_allowed(cls, phone_number: str) -> bool:
        key = cls._key(phone_number)
        attempts = cache.get(key, 0)
        return attempts < cls.MAX_ATTEMPTS

    @classmethod
    def increment(cls, phone_number: str) -> int:
        key = cls._key(phone_number)
        attempts = cache.get(key, 0)
        attempts += 1
        if attempts == 1:
            cache.set(key, attempts, timeout=cls.WINDOW_SECONDS)
        else:
            cache.set(key, attempts, timeout=cls.WINDOW_SECONDS)
        return attempts

    @classmethod
    def remaining(cls, phone_number: str) -> int:
        key = cls._key(phone_number)
        attempts = cache.get(key, 0)
        return max(0, cls.MAX_ATTEMPTS - attempts)

    @classmethod
    def reset(cls, phone_number: str):
        key = cls._key(phone_number)
        cache.delete(key)
