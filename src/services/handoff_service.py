"""
Service layer for responsibility handoffs.

This module enforces workflow rules and state transitions.
It intentionally does not handle persistence, authentication,
or transport concerns.
"""
from sqlalchemy.orm import Session
from core.database import SessionLocal

from domain.models import Handoff, HandoffEvent
from domain.state import handoffs
from exceptions.handoff import (
    InvalidStateTransition,
    UnauthorizedActor,
    HandoffNotFound
)

# TODO: create repo abstractions


def initiate_handoff(handoff_id: int, actor: str, receiving_party: str) -> dict:
    db: Session = SessionLocal()
    try:
        handoff = db.get(Handoff, handoff_id)
        if not handoff:
            raise HandoffNotFound()
        if handoff.state != "active":
            raise InvalidStateTransition(f"Cannot accept transfer from state '{handoff['state']}'")
        if handoff.current_owner != actor:
            raise UnauthorizedActor(f"Receiving party '{actor}' unauthorized")
        
        handoff.state = "pending"
        handoff.receiving_party = receiving_party
        
        event = HandoffEvent(
            handoff_id = handoff.id,
            action = "initiate",
            actor = actor,
            from_state = "active",
            to_state = "pending",
        )
        db.add(event)
        
        db.commit()
        db.refresh(handoff)
        return handoff
    
    except Exception:
        db.rollback()
        raise
        
    finally:
        db.close()

def accept_handoff(handoff_id: int, actor: str) -> dict:
    db: Session = SessionLocal()
    try:
        handoff = db.get(Handoff, handoff_id)
        if not handoff:
            raise HandoffNotFound()
        if handoff.state != "pending":
            raise InvalidStateTransition(f"Cannot accept transfer from state '{handoff['state']}'")
        if handoff.receiving_party != actor:
            raise UnauthorizedActor(f"Receiving party '{actor}' unauthorized")
        
        previous_owner = handoff.current_owner
        
        handoff.current_owner = actor
        handoff.state = "active"
        handoff.receiving_party = None
        
        event = HandoffEvent(
            handoff_id = handoff.id,
            action = "accept",
            actor = actor,
            from_state = "pending",
            to_state = "active",
            previous_owner = previous_owner,
            new_owner = actor,
        )
        db.add(event)
        
        db.commit()
        db.refresh(handoff)
        return handoff
    
    except Exception:
        db.rollback()
        raise
    
    finally:
        db.close()

def decline_handoff(handoff_id: int, actor: str) -> dict:
    db: Session = SessionLocal()
    try:
        handoff = db.get(Handoff, handoff_id)
        if not handoff:
            raise HandoffNotFound()
        if handoff.state != "pending":
            raise InvalidStateTransition(f"Cannot accept transfer from state '{handoff['state']}'")
        if handoff.current_owner != actor:
            raise UnauthorizedActor(f"Receiving party '{actor}' unauthorized")
        
        handoff.state = "active"
        handoff.receiving_party = None
    
        event = HandoffEvent(
            handoff_id = handoff.id,
            action = "decline",
            actor = actor,
            from_state = "pending",
            to_state = "active",
        )
        db.add(event)
        
        db.commit()
        db.refresh(handoff)
        return handoff
    
    except Exception:
        db.rollback()
        raise
    
    finally:
        db.close()

def create_handoff(current_owner: str) -> Handoff:
    db: Session = SessionLocal()
    try:
        handoff = Handoff(
            current_owner=current_owner,
            state="active",
        )
        db.add(handoff)
        db.flush()
        
        event = HandoffEvent(
            handoff_id=handoff.id,
            action="create",
            actor=current_owner,
            to_state="active",
        )
        db.add(event)
        
        db.commit()
        db.refresh(handoff)
        return handoff
    
    except Exception:
        db.rollback()
        raise
    
    finally:
        db.close()