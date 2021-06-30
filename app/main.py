from fastapi.middleware.cors import CORSMiddleware

import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware


# Set all CORS enabled origins
from app import app
from app.settings import settings


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


#Note: https://github.com/getsentry/sentry-python/issues/947#issuecomment-746616538
if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=1.0, attach_stacktrace=True, request_bodies='always')
    app.add_middleware(SentryAsgiMiddleware)
    import gitcommit
    sentry_sdk.set_tag("api-project-name", settings.SENTRY_PROJECT_NAME)
    sentry_sdk.set_tag("api-server-name", settings.SENTRY_SERVER_NAME)
    sentry_sdk.set_tag("api-chain-id", settings.CHAIN_ID)
    sentry_sdk.set_tag("api-git-dt", gitcommit.date)
    sentry_sdk.set_tag("api-git-branch", gitcommit.branch or "main")


from app.api import graphql
from app.api import http
