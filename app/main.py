import os
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI
from pydantic import BaseModel

DSN = os.getenv("DATABASE_URL", "postgresql://tickets:tickets@localhost:5432/tickets")
FIELDS = ("id", "title", "site", "priority")


@asynccontextmanager
async def lifespan(app):
    with psycopg.connect(DSN) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS tickets (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                site TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'P3')"""
        )
    yield


app = FastAPI(lifespan=lifespan)


class Ticket(BaseModel):
    title: str
    site: str
    priority: str = "P3"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tickets")
def list_tickets():
    with psycopg.connect(DSN) as conn:
        rows = conn.execute("SELECT id, title, site, priority FROM tickets ORDER BY id").fetchall()
    return [dict(zip(FIELDS, r)) for r in rows]


@app.post("/tickets", status_code=201)
def create_ticket(t: Ticket):
    with psycopg.connect(DSN) as conn:
        row = conn.execute(
            "INSERT INTO tickets (title, site, priority) VALUES (%s, %s, %s) RETURNING id",
            (t.title, t.site, t.priority),
        ).fetchone()
    return {"id": row[0], **t.model_dump()}