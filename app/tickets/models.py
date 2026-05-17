from datetime import datetime
from sqlalchemy import (
    String,
    Float,
    ForeignKey,
    DateTime,
    Boolean,
    Integer,
    Text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.core.database import Base


class SupportTicket(Base):

    __tablename__="support_tickets"

    id:Mapped[int]=mapped_column(
        primary_key=True
    )

    ticket_number:Mapped[str]=mapped_column(
        unique=True,
        index=True
    )

    user_id:Mapped[int]=mapped_column(
        ForeignKey("users.id")
    )

    order_id:Mapped[int|None]=mapped_column(
        ForeignKey("orders.id"),
        nullable=True
    )

    issue:Mapped[str]

    category:Mapped[str]=mapped_column(
        default="general"
    )

    priority:Mapped[str]=mapped_column(
        default="medium"
    )

    assigned_to:Mapped[
        str|None
    ]=mapped_column(
        nullable=True
    )

    status:Mapped[str]=mapped_column(
        default="open"
    )

    resolution:Mapped[
        str|None
    ]=mapped_column(
        nullable=True
    )

    created_at:Mapped[
        datetime
    ]=mapped_column(
        default=datetime.utcnow
    )

    updated_at:Mapped[
        datetime
    ]=mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )