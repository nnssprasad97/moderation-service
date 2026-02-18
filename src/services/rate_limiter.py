# Token bucket rate limiter implementation using Redis for distributed rate limiting
import time
import redis.asyncio as redis
from src.config import settings

# RateLimiter class implementing token bucket algorithm with Redis
c
    # Initialize rate limiter with Redis connection and configurationlass RateLimiter:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        self.capacity = settings.RATE_LIMIT_CAPACITY
        self.rate = settings.RATE_LIMIT_REFILL_RATE / 60.0  # tokens per second

    # Check if user has available tokens based on rate limit policy
    async def is_allowed(self, user_id: str) -> bool:
        key = f"rate_limit:{user_id}"
        now = time.time()
        
        # Lua script to perform token bucket check atomically
        # KEYS[1] = bucket key
        # ARGV[1] = capacity
        # ARGV[2] = rate (tokens/sec)
        # ARGV[3] = current timestamp
        script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        local last_tokens = tonumber(redis.call("hget", key, "tokens"))
        local last_refreshed = tonumber(redis.call("hget", key, "last_refreshed"))

        if last_tokens == nil then
            last_tokens = capacity
            last_refreshed = now
        end

        local delta = math.max(0, now - last_refreshed)
        local filled_tokens = math.min(capacity, last_tokens + (delta * rate))

        if filled_tokens >= 1 then
            local new_tokens = filled_tokens - 1
            redis.call("hset", key, "tokens", new_tokens, "last_refreshed", now)
            redis.call("expire", key, 60) -- Expire key if inactive
            return 1 -- Allowed
        else
            return 0 -- Rejected
        end
        """
        result = await self.redis.eval(script, 1, key, self.capacity, self.rate, now)
        return result == 1
