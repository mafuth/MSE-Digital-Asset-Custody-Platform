from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from lib.database.main import create_db_and_tables, engine, get_session
from lib.database.models.metal import Metal
from routes.v1 import auth, metals, transactions, accounts, public, admin, vaults
from lib.websocket_manager import manager
from lib.logger import logger
import json
import asyncio
import random
from datetime import datetime
from contextlib import asynccontextmanager
import uvicorn

# Lifespan manager for modern FastAPI startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Bare Metals Pvt. API Backend (Lifespan)...")
    create_db_and_tables()
    logger.info("Database tables created/verified.")
    
    
    yield
    
    # Shutdown logic

app = FastAPI(title="Bare Metals Pvt. API", lifespan=lifespan)

# CORSMiddleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(metals.router)
app.include_router(transactions.router)
app.include_router(accounts.router)
app.include_router(public.router)
app.include_router(admin.router)
app.include_router(vaults.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Bare Metals Pvt. Modernization API V1","Swagger UI": "/docs","ReDoc": "/redoc"}

@app.websocket("/api/v1/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Just keep the connection alive
            data = await websocket.receive_text()
            # Echo for testing
            await manager.send_personal_message(f"Message received: {data}", user_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
