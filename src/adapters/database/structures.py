from typing import Optional, List

from sqlalchemy import BigInteger, String, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    tg_username: Mapped[str] = mapped_column(String(50))
    surname: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(30))
    patronymic: Mapped[str] = mapped_column(String(30))
    number: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    posts: Mapped[List["Post"]] = relationship(
        "Post",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    __table_args__ = (
        Index('ix_unique_user_tg_id', 'tg_id', unique=True),
    )


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    text: Mapped[str] = mapped_column(String(1000))
    image_link: Mapped[str] = mapped_column(String(500))
    is_checked: Mapped[bool]

    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="posts"
    )