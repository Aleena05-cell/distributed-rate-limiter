import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from .limiter import TokenBucketLimiter

app = FastAPI()
limiter = TokenBucketLimiter(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    capacity=int(os.getenv("CAPACITY", 20)),
    rate=float(os.getenv("RATE", 5)),
)

def client_id(request: Request) -> str:
    key = request.headers.get("x-api-key")
    if key:
        return key
    fwd = request.headers.get("x-forwarded-for")
    return fwd.split(",")[0].strip() if fwd else request.client.host

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    try:
        allowed, tokens = await limiter.check(client_id(request))
    except RedisError:
        return await call_next(request)  # fail open; log this in a real version

    if not allowed:
        return JSONResponse(
            {"detail": "Too many requests"},
            status_code=429,
            headers={"Retry-After": "1", "X-RateLimit-Remaining": "0"},
        )
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(int(tokens))
    return response

@app.get("/ping")
async def ping():
    return {"ok": True}