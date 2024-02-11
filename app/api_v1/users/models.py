from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api_v1.users.schemas import UserShow
from app.db import Base


class User(Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[bytes]
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)

    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)
    orders: Mapped["Order"] = relationship(back_populates="user")
    cart: Mapped["Cart"] = relationship(back_populates="user", uselist=False)

    def __str__(self):
        return f"Пользователь {self.email}"

    def to_read_model(self) -> UserShow:
        return UserShow(
            id=self.id,
            username=self.username,
            email=self.email
        )
