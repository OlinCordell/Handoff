"""
Service layer for responsibility handoffs.

This module enforces workflow rules and state transitions.
It intentionally does not handle persistence, authentication,
or transport concerns.
"""
from sqlalchemy.orm import Session
from core.database import SessionLocal

from domain.models import Handoff, HandoffEvent
from exceptions.handoff import (
    InvalidStateTransition,
    UnauthorizedActor,
    HandoffNotFound
)

from domain.enums import HandoffAction
from domain.enums import HandoffState

# TODO: create repo abstractions
# define enums...


def initiate_handoff(handoff_id: int, actor: str, receiving_party: str) -> dict:
    db: Session = SessionLocal()
    try:
        handoff = get_handoff_for_update(db, handoff_id)
        if handoff.state != HandoffState.ACTIVE:
            raise InvalidStateTransition(f"Cannot accept transfer from state '{handoff['state']}'")
        if handoff.current_owner != actor:
            raise UnauthorizedActor("Cannot initiate transfer")
        
        handoff.state = HandoffState.PENDING
        handoff.receiving_party = receiving_party
        
        record_event(
            db,
            handoff,
            action=HandoffAction.INITIATE,
            actor=actor,
            from_state=HandoffState.ACTIVE,
            to_state=HandoffState.PENDING,
        )
        
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
        handoff = get_handoff_for_update(db, handoff_id)
        if handoff.state != HandoffState.PENDING:
            raise InvalidStateTransition(f"Cannot accept transfer from state '{handoff['state']}'")
        if handoff.receiving_party != actor:
            raise UnauthorizedActor("Cannot accept transfer")
        
        previous_owner = handoff.current_owner
        
        handoff.current_owner = actor
        handoff.state = HandoffState.ACTIVE
        handoff.receiving_party = None
        
        record_event(
            db,
            handoff,
            action=HandoffAction.ACCEPT,
            actor=actor,
            from_state=HandoffState.PENDING,
            to_state=HandoffState.ACTIVE,
            previous_owner=previous_owner,
            new_owner=actor,
        )
        
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
        handoff = get_handoff_for_update(db, handoff_id)
        if handoff.state != HandoffState.PENDING:
            raise InvalidStateTransition(f"Cannot accept transfer from state '{handoff['state']}'")
        if handoff.receiving_party != actor:
            raise UnauthorizedActor("Cannot decline transfer")
        
        handoff.state = HandoffState.ACTIVE
        handoff.receiving_party = None
        
        record_event(
            db,
            handoff,
            action=HandoffAction.DECLINE,
            actor=actor,
            from_state=HandoffState.PENDING,
            to_state=HandoffState.ACTIVE,
        )
        
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
            state=HandoffState.ACTIVE,
        )
        db.add(handoff)
        db.flush()
        
        record_event(
            db,
            handoff,
            action=HandoffAction.CREATE,
            actor=current_owner,
            to_state=HandoffState.ACTIVE,
        )
        
        db.commit()
        db.refresh(handoff)
        return handoff
    
    except Exception:
        db.rollback()
        raise
    
    finally:
        db.close()

# no locking
def get_handoff(handoff_id: int) -> Handoff:
    db: Session = SessionLocal()
    try:
        handoff = db.query(Handoff).filter(Handoff.id == handoff_id).one_or_none()
        if handoff is None:
            raise HandoffNotFound(f"Handoff {handoff_id} not found")
        return handoff
    finally:
        db.close()
        
def get_handoff_for_update(db: Session, handoff_id: int) -> Handoff:
    handoff = (db.query(Handoff).filter(Handoff.id == handoff_id)
               .with_for_update().one_or_none())
    if handoff is None:
        raise HandoffNotFound(f"Handoff {handoff_id} not found")
    return handoff

def record_event(db: Session, handoff: Handoff, *, action: HandoffAction, actor: str,
                 from_state: HandoffState | None = None, to_state: HandoffState, 
                 previous_owner: str | None = None, new_owner: str | None = None) -> None:
    event = HandoffEvent(
        handoff_id=handoff.id,
        action=action,
        actor=actor,
        from_state=from_state,
        to_state=to_state,
        previous_owner=previous_owner,
        new_owner=new_owner,
    )
    db.add(event)
    
def assert_transition_allowed():
    pass

def cancel_pending_handoff():
    pass

def list_handoffs_for_user():
    pass