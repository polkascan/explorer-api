import os
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, HttpUrl, validator


default_env_ext = ".env"
local_env_ext = ".local.env"


class Settings(BaseSettings):
    CHAIN_ID: str
    HTTP_MOUNT: str = "/graphql"
    WS_MOUNT: str = "/graphql-ws"
    API_STR: str = "/api/"
    SERVER_ADDR: str
    SERVER_PORT: int
    WEBSOCKET_URI: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    API_SQLA_URI: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_HARVESTER_NAME: str
    DEFAULT_PAGE_SIZE: int = 10
    BROADCAST_URI: str
    BLOCK_LIMIT_COUNT: int

    SENTRY_PROJECT_NAME: str
    SENTRY_SERVER_NAME: str
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

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
