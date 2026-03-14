"""
Polymolt — FastAPI application entry point.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.regions import router as regions_router
from app.api.market import router as market_router
from app.api.ws import router as ws_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Polymolt",
    description="Real-time prediction market for regional sustainability",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(regions_router)
app.include_router(market_router)
app.include_router(ws_router)


@app.get("/")
def root():
    return {
        "name": "Polymolt API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
