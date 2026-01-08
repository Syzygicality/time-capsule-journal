from app.users.routers import router

from fastapi import FastAPI

app = FastAPI(title="Time Capsule Journal")

app.include_router(router)