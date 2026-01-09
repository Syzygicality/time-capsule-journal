from app.users.routers import router

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

app = FastAPI(title="Time Capsule Journal")

app.include_router(router)

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"detail": str(exc)})