import os
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, HttpUrl, validator

default_env_ext = ".env"
local_env_ext = ".local.env"


class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    SERVER_NAME: str
    SERVER_ADDR: str
    SERVER_PORT: int
    WEBSOCKET_ADDR: str
    WEBSOCKET_PORT: int
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    API_SQLA_DIALECT: str
    API_SQLA_DRIVER: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    POLLING_REDIS_HOST: str
    POLLING_REDIS_PORT: int

    SENTRY_DSN: Optional[HttpUrl] = None

    def __init__(self, *args, **kwargs):
        default_kws = {}
        env_file = self.__config__.env_file
        if env_file is not None and env_file.endswith(default_env_ext):
            local_env_file = env_file[:-len(default_env_ext)] + local_env_ext
            if os.path.exists(local_env_file):
                default_kws["_env_file"] = local_env_file
        default_kws.update(kwargs)
        super().__init__(*args, **default_kws)

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    @property
    def sqla_uri(self):
        return f"{self.API_SQLA_DIALECT}+{self.API_SQLA_DRIVER}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def WEBSOCKET_URI(self):
        base = self.WEBSOCKET_ADDR
        if self.WEBSOCKET_PORT:
            base += f":{self.WEBSOCKET_PORT}"
        return base

    @property
    def SERVER_URI(self):
        base = self.SERVER_ADDR
        if self.SERVER_PORT:
            base += f":{self.SERVER_PORT}"
        return base

    @property
    def SERVER_HOST(self):
        base = f"https://{self.SERVER_URI}"
        if self.SERVER_PORT:
            base += f":{self.SERVER_PORT}"
        return base

    @property
    def broadcast_uri(self):
        return f"redis://{self.POLLING_REDIS_HOST}:{self.POLLING_REDIS_PORT}"

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
