"""
Service layer for responsibility handoffs.

This module enforces workflow rules and state transitions.
It intentionally does not handle persistence, authentication,
or transport concerns.
"""

from domain.state import handoffs
from exceptions.handoff import (
    InvalidStateTransition,
    UnauthorizedActor,
    HandoffNotFound
)

# TODO: create repo abstractions


def initiate_handoff(handoff_id: int, actor: str, receiving_party: str) -> dict:
    handoff = handoffs.get(handoff_id)

    if not handoff:
        raise HandoffNotFound()
    if handoff["state"] != "active":
        raise InvalidStateTransition(f"Cannot initiate transfer from state '{handoff['state']}'")
    if handoff["current_owner"] != actor:
        raise UnauthorizedActor(f"Initiating party '{actor}' unauthorized")
    handoff["state"] = "pending"
    handoff["initiated_by"] = actor
    handoff["receiving_party"] = receiving_party
    
    handoff["events"].append({
        "action": "initiate",
        "actor": actor,
        "from_state": "active",
        "to_state": "pending",
        "to": receiving_party
    })
    
    return handoff

def accept_handoff(handoff_id: int, actor: str) -> dict:
    handoff = handoffs.get(handoff_id)
    
    if not handoff:
        raise HandoffNotFound()
    if handoff["state"] != "pending":
        raise InvalidStateTransition(f"Cannot accept transfer from state '{handoff['state']}'")
    if handoff["receiving_party"] != actor:
        raise UnauthorizedActor(f"Receiving party '{actor}' unauthorized")
    
    previous_owner = handoff["current_owner"]
    handoff["state"] = "accepted"
    handoff["current_owner"] = actor
    handoff["events"].append({
        "action": "accept",
        "actor": actor,
        "from_state": "pending",
        "to_state": "accepted",
        "previous_owner": previous_owner,
        "new_owner": actor
    })
    
    return handoff

def decline_handoff(handoff_id: int, actor: str) -> dict:
    handoff = handoffs.get(handoff_id)
    
    if not handoff:
        raise HandoffNotFound()
    if handoff["state"] != "pending":
        raise InvalidStateTransition(f"Cannot decline transfer from state '{handoff['state']}'")
    if handoff["receiving_party"] != actor:
        raise UnauthorizedActor(f"Receiving party '{actor}' unauthorized")
    
    handoff["receiving_party"] = None
    handoff["state"] = "active"
    handoff["events"].append({
        "action": "decline",
        "actor": actor,
        "from_state": "pending",
        "to_state": "active",
    })
    
    return handoff