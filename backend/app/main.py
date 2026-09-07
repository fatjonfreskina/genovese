from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import groups, expenses, balances, members, settlements, email_links
import os

allow_origins = os.getenv("ALLOW_ORIGINS", "")
origins = [o.strip() for o in allow_origins.split(",") if o.strip()]

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Equa API", version="1.7.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(groups.router)
app.include_router(expenses.router)
app.include_router(balances.router)
app.include_router(members.router)
app.include_router(settlements.router)
app.include_router(email_links.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": "equa"}
