from fastapi import FastAPI
from app.routers.api_summary import router as summary_router
from app.routers.api_quiz import router as quiz_router

app = FastAPI(title="YouTube AI Learning API")

app.include_router(summary_router)
app.include_router(quiz_router)


@app.get("/")
def root():
    return {"message": "YouTube AI Learning API. Visita /docs para la documentación."}
