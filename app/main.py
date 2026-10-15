from fastapi import FastAPI

from app.routers.price_history import router

app = FastAPI()
app.include_router(router)
