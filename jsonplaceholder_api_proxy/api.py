from fastapi import FastAPI
import importlib.metadata

from .posts import posts_router
from .users import users_router

app = FastAPI(
    title="JSON Placeholder API Proxy",
    version=importlib.metadata.version("jsonplaceholder-api-proxy"),
)
app.include_router(users_router, prefix="/users")
app.include_router(posts_router, prefix="/posts")
