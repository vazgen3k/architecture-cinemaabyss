import random

from fastapi import FastAPI, Request, Response
import os
import httpx
app = FastAPI()


PORT = int(os.getenv('PORT', '8000'))
MONOLITH_URL = os.getenv('MONOLITH_URL').rstrip('/')
MOVIES_SERVICE_URL = os.getenv('MOVIES_SERVICE_URL').rstrip('/')
GRADUAL_MIGRATION = os.getenv('GRADUAL_MIGRATION', 'false').lower() == 'true'
MOVIES_MIGRATION_PERCENT = int(os.getenv('MOVIES_MIGRATION_PERCENT', '0'))


def should_route_to_movies_service() -> bool:
    if not GRADUAL_MIGRATION:
        return False

    percent = MOVIES_MIGRATION_PERCENT

    if percent <= 0:
        return False
    if percent >= 100:
        return True

    return random.randint(1, 100) <= percent
@app.api_route("/api/movies", methods=["GET", "POST"])
async def proxy_movies(request: Request):
    monolith_url = MONOLITH_URL
    movies_service_url = MOVIES_SERVICE_URL

    target_base = (movies_service_url if should_route_to_movies_service() else monolith_url)

    target_url = f"{target_base}/api/movies"
    print(target_url)
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            params=request.query_params,
            content=await request.body(),
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_all(request: Request, path: str):
    monolith_url = os.getenv("MONOLITH_URL")

    target_url = f"{monolith_url}/{path}"

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            params=request.query_params,
            content=await request.body(),
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )