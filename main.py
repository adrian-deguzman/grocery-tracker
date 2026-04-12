from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routes import router as cart_router

app = FastAPI(title="Grocery Tracker API")

# 1. Include API routes FIRST
app.include_router(cart_router)

# 2. Mount static files (Frontend) LAST
# By mounting at "/", index.html is served automatically at your root domain.
app.mount("/", StaticFiles(directory="static", html=True), name="static")