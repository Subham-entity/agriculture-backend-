from fastapi import FastAPI
from .database import engine, Base
from .routers import marketplace, orders, ai_engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Direct Agri-Marketplace API")

# Register Endpoints
app.include_router(marketplace.router)
app.include_router(orders.router)
app.include_router(ai_engine.router)  # Mounted Day 3 Router

@app.get("/")
def health_check():
    return {"status": "Active", "message": "Day 3 AI Engine & Route Optimization Integrated"}