from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP
from sqlalchemy import UUID as _UUID
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UsersShows(Base):
    __tablename__ = "users_shows"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)
    show_id: Mapped[UUID] = mapped_column(
        ForeignKey("show.id"), primary_key=True
    )
    user: Mapped["User"] = relationship(back_populates="shows")
    show: Mapped["Show"] = relationship(back_populates="users")


class Place(Base):
    __tablename__ = "place"
    id: Mapped[UUID] = mapped_column(
        _UUID, primary_key=True, default=uuid4(), nullable=False
    )
    hall_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    shows: Mapped[list["Show"]] = relationship("Show", back_populates="place")


class Show(Base):
    __tablename__ = "show"
    id: Mapped[UUID] = mapped_column(
        _UUID, primary_key=True, default=uuid4(), nullable=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    place_id = mapped_column(ForeignKey("place.id"), nullable=False)
    place: Mapped["Place"] = relationship("Place", back_populates="shows")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="show")
    users: Mapped[list["UsersShows"]] = relationship(
        back_populates="show"
    )


class Event(Base):
    __tablename__ = "event"
    id: Mapped[UUID] = mapped_column(_UUID, primary_key=True, default=uuid4())
    datetime: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    show_id = mapped_column(ForeignKey("show.id"), nullable=False)
    show: Mapped["Show"] = relationship("Show", back_populates="events")
    url_number: Mapped[int] = mapped_column(Integer, nullable=False)
    tickets: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class User(Base):
    __tablename__ = "user"
    id: Mapped[UUID] = mapped_column(_UUID, primary_key=True, default=uuid4())
    chat_id: Mapped[int] = mapped_column(Integer, nullable=False)
    subscription: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    shows: Mapped[list["UsersShows"]] = relationship(
        back_populates="user")