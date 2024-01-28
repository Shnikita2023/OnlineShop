from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Profile(Base):
    __tablename__ = "profile"

    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    bio: Mapped[str | None]

    user_id: Mapped[int] = mapped_column(ForeignKey(column="user.id", ondelete="CASCADE"), unique=True)
    user = relationship(argument="User", back_populates="profile")
