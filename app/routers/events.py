from fastapi import APIRouter, HTTPException
from typing import List
from sqlmodel import select
from app.data.db import SessionDep
from app.models.event import Event
from app.models.user import User
from app.models.registration import Registration

router = APIRouter(tags=["events"])


@router.get("/events", response_model=List[Event])
def get_events(session: SessionDep) -> List[Event]:
    """
    Restituisce la lista di tutti gli eventi esistenti.

    Recupera in modo persistente tramite SQLModel e SQLite tutti gli eventi
    creati nel sistema
    """
    events = session.exec(select(Event)).all()
    return list(events)


@router.post("/events", response_model=Event, status_code=201)
def create_event(event: Event, session: SessionDep) -> Event:
    """
    Crea un nuovo evento.

    Riceve in input i dati del nuovo evento (title, description, date, location),
    li valida tramite Pydantic/SQLModel e salva l'evento nel database SQLite.
    Restituisce l'evento salvato, includendo l'id generato.
    """
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.put("/events/{event_id}", response_model=Event)
def update_event(event_id: int, event_update: Event, session: SessionDep) -> Event:
    """
    Aggiorna un evento esistente.

    Cerca l'evento tramite ID. Se non esiste, restituisce 404.
    Altrimenti aggiorna i suoi dati persistendoli nel database SQLite.
    """
    db_event = session.get(Event, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    event_data = event_update.model_dump(exclude_unset=True)
    for key, value in event_data.items():
        setattr(db_event, key, value)

    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event

@router.delete("/events")
def delete_all_events(session: SessionDep):
    """
    Elimina tutti gli eventi esistenti nel database.
    """
    events = session.exec(select(Event)).all()
    for event in events:
        session.delete(event)
    session.commit()
    return {"message": "All events deleted successfully"}


@router.delete("/events/{event_id}")
def delete_event(event_id: int, session: SessionDep):
    """
    Elimina l'evento con l'id indicato e tutte le registrazioni associate.

    Cerca l'evento. Se non esiste, restituisce 404 Not Found.
    Altrimenti, elimina prima tutte le registrazioni collegate
    e poi l'evento stesso dal database SQLite.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Manual cascade delete for registrations
    registrations = session.exec(select(Registration).where(Registration.event_id == event_id)).all()
    for reg in registrations:
        session.delete(reg)

    session.delete(event)
    session.commit()
    return {"message": "Event and associated registrations deleted successfully"}
