from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.sql import func

from core.database import Base

class Handoff(Base):
    __tablename__ = "handoffs"
    
    id = Column(Integer, primary_key=True)
    
    current_owner = Column(Text, nullable=False)
    receiving_party = Column(Text, nullable=False)
    
    state = Column(Text, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    __table_args__ = (
        CheckConstraint(
            "state IN ('active', 'pending', 'accepted')",
            name="handoff_state_check",
        ),
    )

class HandoffEvent(Base):
    __tablename__ = "handoff_events"
    
    id = Column(Integer, primary_key=True)
    
    handoff_id = Column(
        Integer,
        ForeignKey("handoffs.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    action = Column(Text, nullable=False)
    actor = Column(Text, nullable=False)
    
    from_state = Column(Text, nullable=True)
    to_state = Column(Text, nullable=True)
    
    previous_owner = Column(Text, nullable=True)
    new_owner = Column(Text, nullable=True)
    
    create_at = Column(DateTime, server_default=func.now(), nullable=False)