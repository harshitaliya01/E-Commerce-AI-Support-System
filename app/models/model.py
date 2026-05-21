from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class Order(Base):

    __tablename__="orders"

    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),index=True)
    order_number:Mapped[str]=mapped_column(String(50),unique=True,index=True)
    product_name:Mapped[str]=mapped_column(String(255))
    quantity:Mapped[int]=mapped_column(default=1)
    total_amount:Mapped[float]=mapped_column(Float)
    shipping_address:Mapped[str]=mapped_column(Text)
    order_status:Mapped[str]=mapped_column(default="processing")
    payment_status:Mapped[str]=mapped_column(default="paid")
    tracking_number:Mapped[str|None]=mapped_column(nullable=True)
    courier_name:Mapped[str|None]=mapped_column(nullable=True)
    estimated_delivery:Mapped[datetime|None]=mapped_column(nullable=True)
    delivered_at:Mapped[datetime|None]=mapped_column(nullable=True)
    refund_status:Mapped[str|None]=mapped_column(default=None)
    refund_window_days:Mapped[int]=mapped_column(default=7)
    support_ticket_count:Mapped[int]=mapped_column(default=0)
    is_cancelled:Mapped[bool]=mapped_column(default=False)
    created_at:Mapped[datetime]=mapped_column(default=datetime.utcnow)
    updated_at:Mapped[datetime]=mapped_column(default=datetime.utcnow,onupdate=datetime.utcnow)


class SupportTicket(Base):

    __tablename__="support_tickets"

    id:Mapped[int]=mapped_column(primary_key=True)
    ticket_number:Mapped[str]=mapped_column(unique=True,index=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"))
    order_id:Mapped[int|None]=mapped_column(ForeignKey("orders.id"),nullable=True)
    issue:Mapped[str]
    category:Mapped[str]=mapped_column(default="general")
    status:Mapped[str]=mapped_column(default="open")
    resolution:Mapped[str|None]=mapped_column(nullable=True)
    created_at:Mapped[datetime]=mapped_column(default=datetime.utcnow)
    updated_at:Mapped[datetime]=mapped_column(default=datetime.utcnow,onupdate=datetime.utcnow)


class Payment(Base):

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"),index=True )
    amount: Mapped[float] = mapped_column(Float)
    method: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20),default="pending")
    transaction_id: Mapped[str | None] = mapped_column(String(100),nullable=True )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Product(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255),index=True,)
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer,default=0,)
    rating: Mapped[float] = mapped_column(Float,default=4.0,)
    image_url: Mapped[str] = mapped_column(String(500),nullable=True,)    


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255),unique=True,index=True,)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,)
    is_admin: Mapped[bool] = mapped_column(Boolean,default=False,)


# class ChatSession(Base):

#     __tablename__ = "chat_sessions"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),unique=True,)
#     created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,)


# class ChatMessage(Base):

#     __tablename__ = "chat_messages"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))
#     role: Mapped[str] = mapped_column(String(50))
#     content: Mapped[str] = mapped_column(Text)
#     created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow,)