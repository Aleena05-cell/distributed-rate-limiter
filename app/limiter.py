import pathlib
import redis.asyncio as redis

LUA = (pathlib.Path(__file__).parent / "scripts/token_bucket.lua").read_text()

class TokenBucketLimiter:
    def __init__(self, url: str, capacity: int, rate: float):
        self.redis = redis.from_url(url)
        self.script = self.redis.register_script(LUA)
        self.capacity = capacity
        self.rate = rate

    async def check(self, client_id: str):
        allowed, tokens = await self.script(
            keys=[f"rl:{client_id}"], args=[self.capacity, self.rate]
        )
        return bool(allowed), float(tokens)