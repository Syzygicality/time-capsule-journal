from app.users.routers import router as user_router
from app.capsules.routers import router as capsule_router

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI(
    title="Time Capsule Journal",
    description="A personal project aimed at providing a modern alternative to the antiquated art of journalling.\n\nGitHub Repo: https://github.com/Syzygicality/time-capsule-journal",
    version="1.0.0",
    docs_url=None,
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="My API Docs",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1
        }
    )

app.include_router(user_router)
app.include_router(capsule_router)

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"detail": str(exc)})