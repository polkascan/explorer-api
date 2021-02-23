from fastapi import FastAPI
from broadcaster import Broadcast

from app.settings import settings


broadcast = Broadcast(settings.broadcast_uri)


app = FastAPI(
    title=settings.PROJECT_NAME,
    on_startup=[broadcast.connect], on_shutdown=[broadcast.disconnect]
)
