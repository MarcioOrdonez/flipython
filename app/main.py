from fastapi import FastAPI

from app.api import feature_flags_router

from app.api import api_keys_router

app = FastAPI()
app.include_router(feature_flags_router)
app.include_router(api_keys_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
