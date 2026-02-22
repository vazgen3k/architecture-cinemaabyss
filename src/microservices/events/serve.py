import logging
import os
import sys

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from faststream.kafka import KafkaBroker
from fastream import FastReam

logger = logging.getLogger("events-service")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)  # ВАЖНО: stdout
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.propagate = False

app = FastAPI()

broker = KafkaBroker(os.getenv("KAFKA_BROKERS", "kafka:9092"))
stream = FastStream(broker)

@app.on_event("startup")
async def on_startup():
    await broker.connect()
    await stream.start()


@app.on_event("shutdown")
async def on_shutdown():
    await broker.close()
    await stream.stop()

@broker.subscriber("movie-events")
async def movie_handler(body):
    logger.info("movie-event: %s", body)


@broker.subscriber("user-events")
async def user_handler(body):
    logger.info("user-event: %s", body)


@broker.subscriber("payment-events")
async def payment_handler(body):
    logger.info("payment-event: %s", body)


@app.get("/api/events/health")
async def health():
    return JSONResponse({"status": True}, status_code=status.HTTP_200_OK)


@app.post("/api/events/user")
async def create_user_event(request: Request):
    payload = await request.body()
    await broker.publish(payload, topic="user-events")
    return JSONResponse({"status": "success"}, status_code=status.HTTP_201_CREATED)


@app.post("/api/events/payment")
async def create_payment_event(request: Request):
    payload = await request.body()
    await broker.publish(payload, topic="payment-events")
    return JSONResponse({"status": "success"}, status_code=status.HTTP_201_CREATED)


@app.post("/api/events/movie")
async def create_movie_event(request: Request):
    payload = await request.body()
    await broker.publish(payload, topic="movie-events")
    return JSONResponse({"status": "success"}, status_code=status.HTTP_201_CREATED)