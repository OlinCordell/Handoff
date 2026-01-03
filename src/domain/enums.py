from enum import Enum

class HandoffState(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    ACCEPTED = "accepted"
    
class HandoffAction(str, Enum):
    CREATE = "create"
    INITIATE = "initiate"
    ACCEPT = "accept"
    DECLINE = "decline"