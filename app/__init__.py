from fastapi import FastAPI
from broadcaster import Broadcast

from app.settings import settings

broadcast = Broadcast(settings.BROADCAST_URI)

app = FastAPI(
    on_startup=[broadcast.connect], on_shutdown=[broadcast.disconnect]
)
