from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers.summary import router as summary_router
from app.routers.quiz import router as quiz_router
from app.core.logging import setup_logging, info
from app.utils.exceptions import APIException

setup_logging()
info("Logging initialized successfully.")

app = FastAPI(title="YouTube AI Learning API")


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


app.include_router(summary_router)
app.include_router(quiz_router)


@app.get("/")
def root():
    """Root endpoint for API health check."""
    return {"message": "YouTube AI Learning API. Visit /docs for documentation."}
