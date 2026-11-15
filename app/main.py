from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.db import get_connection, init_db


class NoteCreate(BaseModel):
    owner: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=120)
    content: str = Field(..., min_length=1, max_length=5000)


class NoteResponse(BaseModel):
    id: int
    owner: str
    title: str
    content: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="CloudVault API",
    description="Lightweight note and snippet service for the CodeMender CI/CD demo.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/notes", response_model=NoteResponse, status_code=201)
def create_note(payload: NoteCreate) -> NoteResponse:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (owner, title, content) VALUES (?, ?, ?)",
            (payload.owner, payload.title, payload.content),
        )
        conn.commit()
        note_id = cursor.lastrowid
        row = conn.execute(
            "SELECT id, owner, title, content FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
    return NoteResponse(**dict(row))


@app.get("/notes", response_model=list[NoteResponse])
def list_notes(owner: str = Query(..., min_length=1, max_length=64)) -> list[NoteResponse]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, owner, title, content FROM notes WHERE owner = ? ORDER BY id DESC",
            (owner,),
        ).fetchall()
    return [NoteResponse(**dict(row)) for row in rows]


@app.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: int) -> NoteResponse:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, owner, title, content FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteResponse(**dict(row))
