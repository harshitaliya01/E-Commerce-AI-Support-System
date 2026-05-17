from datetime import datetime
from sqlalchemy import (
    String,
    Float,
    ForeignKey
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.core.database import Base


class Payment(Base):

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        index=True
    )

    amount: Mapped[float] = mapped_column(
        Float
    )

    method: Mapped[str] = mapped_column(
        String(50)
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending"
    )

    transaction_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow
    )