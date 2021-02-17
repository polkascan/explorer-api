from fastapi import FastAPI
from broadcaster import Broadcast

from app.settings import settings


broadcast = Broadcast(settings.REDIS_URI)


app = FastAPI(
    title=settings.PROJECT_NAME,
    on_startup=[broadcast.connect], on_shutdown=[broadcast.disconnect]
)
