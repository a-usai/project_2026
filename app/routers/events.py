from fastapi import APIRouter, HTTPException
from typing import List
from sqlmodel import select
from app.data.db import SessionDep
from app.models.event import Event
from app.models.user import User
from app.models.registration import Registration
from app.routers.users import UserCreate
from pydantic import BaseModel, ConfigDict
from datetime import datetime

router = APIRouter(tags=["events"])

class EventCreate(BaseModel):
    model_config = ConfigDict(strict=True)
    title: str
    description: str
    date: str  # ISO format datetime string
    location: str

    @property
    def validate_date(self):
        try:
            datetime.fromisoformat(self.date)
        except (ValueError,TypeError):
            raise ValueError("Invalid datetime format")


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
def create_event(event: EventCreate, session: SessionDep) -> Event:
    """
    Crea un nuovo evento.

    Riceve in input i dati del nuovo evento (title, description, date, location),
    li valida tramite Pydantic/SQLModel e salva l'evento nel database SQLite.
    Restituisce l'evento salvato, includendo l'id generato.
    """
    try:
        event.validate_date
    except ValueError:
        raise HTTPException(status_code=422, detail="datetime format not valid")

    db_event = Event(
        title=event.title,
        description=event.description,
        date=datetime.fromisoformat(event.date),
        location=event.location
    )
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event

@router.get("/events/{event_id}", response_model=Event)
def get_event(event_id: int, session: SessionDep) -> Event:
    """Get a specific event by ID."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/events/{event_id}", response_model=Event)
def update_event(event_id: int, event: EventCreate, session: SessionDep) -> Event:
    """
    Aggiorna un evento esistente.

    Cerca l'evento tramite ID. Se non esiste, restituisce 404.
    Altrimenti aggiorna i suoi dati persistendoli nel database SQLite.
    """
    db_event = session.get(Event, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    try:
        event.validate_date
    except (ValueError, TypeError):
        raise HTTPException(status_code=422, detail="Invalid datetime format")

    event_data = event.model_dump(exclude_unset=True)
    for key, value in event_data.items():
        if key == "date":
            value = datetime.fromisoformat(value)
        setattr(db_event, key, value)

    try:
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        return db_event
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

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

@router.post("/events/{event_id}/register", status_code=201)
def register_to_event(event_id: int, user_data: UserCreate, session: SessionDep):
    """Register a user to an event."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    user = session.get(User, user_data.username)
    if not user:
        user = User(username=user_data.username, name=user_data.name, email=user_data.email)
        session.add(user)
        session.commit()
        session.refresh(user)

    reg = session.get(Registration, (user.username, event_id))
    if not reg:
        reg = Registration(username=user.username, event_id=event_id)
        session.add(reg)
        session.commit()
        session.refresh(reg)

    return reg