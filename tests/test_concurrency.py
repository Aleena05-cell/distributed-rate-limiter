import asyncio, httpx, pytest

@pytest.mark.asyncio
async def test_limit_holds_across_instances():
    async with httpx.AsyncClient(base_url="http://localhost:8080") as c:
        headers = {"x-api-key": "test-user-1"}
        results = await asyncio.gather(
            *[c.get("/ping", headers=headers) for _ in range(100)]
        )
    allowed = sum(r.status_code == 200 for r in results)
    # capacity is 20, plus a few refilled tokens during the burst
    assert 20 <= allowed <= 25