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
import app.auth.models

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)


from app.core.database import Base


class Order(Base):

    __tablename__="orders"

    id:Mapped[int]=mapped_column(
        primary_key=True
    )

    user_id:Mapped[int]=mapped_column(
        ForeignKey("users.id"),
        index=True
    )

    order_number:Mapped[str]=mapped_column(
        String(50),
        unique=True,
        index=True
    )

    product_name:Mapped[str]=mapped_column(
        String(255)
    )

    quantity:Mapped[int]=mapped_column(
        default=1
    )

    total_amount:Mapped[float]=mapped_column(
        Float
    )

    shipping_address:Mapped[str]=mapped_column(
        Text
    )

    order_status:Mapped[str]=mapped_column(
        default="processing"
    )

    payment_status:Mapped[str]=mapped_column(
        default="paid"
    )

    tracking_number:Mapped[str|None]=mapped_column(
        nullable=True
    )

    courier_name:Mapped[str|None]=mapped_column(
        nullable=True
    )

    estimated_delivery:Mapped[
        datetime|None
    ]=mapped_column(
        nullable=True
    )

    delivered_at:Mapped[
        datetime|None
    ]=mapped_column(
        nullable=True
    )

    refund_status:Mapped[
        str|None
    ]=mapped_column(
        default=None
    )

    refund_window_days:Mapped[
        int
    ]=mapped_column(
        default=7
    )

    support_ticket_count:Mapped[
        int
    ]=mapped_column(
        default=0
    )

    is_cancelled:Mapped[
        bool
    ]=mapped_column(
        default=False
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