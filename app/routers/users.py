from fastapi import APIRouter, HTTPException
from typing import List
from sqlmodel import select
from app.data.db import SessionDep
from app.models.user import User
from app.models.registration import Registration
from pydantic import BaseModel

router = APIRouter(tags=["users"])

class UserCreate(BaseModel):
    username: str
    name: str
    email: str


@router.get("/users", response_model=List[User])
def get_users(session: SessionDep) -> List[User]:
    """
    Restituisce la lista di tutti gli utenti esistenti.

    Interroga il database SQLite tramite SQLModel per recuperare
    tutti i record dalla tabella degli utenti.
    """
    users = session.exec(select(User)).all()
    return list(users)

@router.get("/users/{username}", response_model=User)
def get_user(username: str, session: SessionDep) -> User:
    """
    Restituisce il singolo utente

    se non esiste, errore 404
    """
    user = session.get(User, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=User, status_code=201)
def create_user(user: UserCreate, session: SessionDep) -> User:
    """
    Crea un nuovo utente.

    Verifica se esiste già un utente con lo stesso username nel database.
    Se esiste, restituisce un errore 409 Conflict.
    Altrimenti, salva l'utente e lo restituisce.
    """
    db_user = session.get(User, user.username)
    if db_user:
        raise HTTPException(status_code=409, detail="User already exists")

    new_user = User(username=user.username, name=user.name, email=user.email)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.delete("/users")
def delete_all_users(session: SessionDep):
    """
    Elimina tutti gli utenti.

    Rimuove in modo persistente tutti gli utenti dal database SQLite.
    """
    users = session.exec(select(User)).all()
    for user in users:
        session.delete(user)
    session.commit()
    return {"message": "All users deleted successfully"}


@router.delete("/users/{username}")
def delete_user(username: str, session: SessionDep):
    """
    Elimina l'utente con lo username indicato e tutte le registrazioni associate.

    Cerca l'utente. Se non esiste, solleva un'eccezione 404 Not Found.
    Altrimenti, elimina in cascata manuale tutte le registrazioni e poi l'utente.
    """
    user = session.get(User, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    registrations = session.exec(select(Registration).where(Registration.username == username)).all()
    for reg in registrations:
        session.delete(reg)

    session.delete(user)
    session.commit()
    return {"message": "User and associated registrations deleted successfully"}


