from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.database import Base


class Product(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text
    )

    category: Mapped[str] = mapped_column(
        String(100)
    )

    price: Mapped[float] = mapped_column(
        Float
    )

    stock: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    rating: Mapped[float] = mapped_column(
        Float,
        default=4.0,
    )

    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
    )