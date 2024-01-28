from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.api_v1.orders import Order
from app.api_v1.users.schemas import UserShow
from app.db import Base


class User(Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(50))
    password: Mapped[bytes]
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)

    profile = relationship(argument="Profile", back_populates="user", uselist=False)
    orders = relationship(argument="Order", back_populates="user")
    cart = relationship(argument="Cart", back_populates="user", uselist=False)

    def to_read_model(self) -> UserShow:
        return UserShow(
            id=self.id,
            username=self.username,
            email=self.email
        )
