from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models
from .routers import groups, expenses, balances, members
import os

allow_origins = os.getenv("ALLOW_ORIGINS")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Equa API", version="1.1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[allow_origins] if allow_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(groups.router)
app.include_router(expenses.router)
app.include_router(balances.router)
app.include_router(members.router)

@app.get("/health")
def health():
    return {"status": "ok", "app": "equa"}