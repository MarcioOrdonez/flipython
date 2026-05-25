from fastapi import FastAPI

from app.api import feature_flags_router

app = FastAPI()
app.include_router(feature_flags_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
