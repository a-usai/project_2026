from fastapi import APIRouter, HTTPException
from typing import List
from sqlmodel import select
from app.data.db import SessionDep
from app.models.registration import Registration

router = APIRouter(tags=["registrations"])

@router.get("/registrations", response_model=List[Registration])
def get_registrations(session: SessionDep) -> List[Registration]:
    """
    Restituisce la lista di tutte le registrazioni esistenti.

    Interroga il database SQLite tramite SQLModel per recuperare
    tutti i record dalla tabella delle registrazioni.
    """
    registrations = session.exec(select(Registration)).all()
    return list(registrations)


@router.delete("/registrations")
def delete_registration(username: str, event_id: int, session: SessionDep):
    """
    Elimina una singola registrazione identificata dai query parameter.

    Se la registrazione non esiste (o se non esistono l'utente/evento corrispondenti),
    solleva un errore 404 Not Found.
    Altrimenti, elimina la registrazione dal database SQLite.
    """
    reg = session.get(Registration, (username, event_id))
    if not reg:
        raise HTTPException(status_code=404, detail="Registration, user, or event not found")

    session.delete(reg)
    session.commit()
    return {"message": "Registration deleted successfully"}
