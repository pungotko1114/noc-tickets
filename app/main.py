from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
tickets: list[dict] = []


class Ticket(BaseModel):
    title: str
    site: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tickets")
def list_tickets():
    return tickets


@app.post("/tickets", status_code=201)
def create_ticket(t: Ticket):
    item = {"id": len(tickets) + 1, **t.model_dump()}
    tickets.append(item)
    return item
