import json
from datetime import datetime, timedelta
from typing import Dict, Any

from sqlalchemy.orm import Mapped, mapped_column

from ORM import Base, Session


__all__ = ["Task", "Notes"]


class Task(Base):

    __tablename__ = 'tasks'

    task_id: Mapped[int] = mapped_column(primary_key=True)
    task_when: Mapped[datetime]
    task_target: Mapped[str]
    task_args: Mapped[str]
    task_is_regular: Mapped[bool]
    task_repeat_delay: Mapped[datetime]
    task_call_after: Mapped[str]
    task_timestamp: Mapped[datetime]

    def __init__(self, when: datetime, target: callable, args: Dict[str, Any] = None, is_regular: bool = False,
                 repeat_delay: datetime = 0, call_after: callable = None):
        super().__init__()
        if when < datetime.utcnow() + timedelta(hours=3):
            raise ValueError('Task can\'t be in past')
        self.task_when = when

        self.task_target = target.__name__
        self.task_args = json.dumps(args)
        self.task_is_regular = is_regular
        self.task_repeat_delay = repeat_delay
        self.task_call_after = call_after.__name__ if call_after else None
        self.task_timestamp = datetime.utcnow() + timedelta(hours=3)
        return

    def add(self):
        """
        Adds task in database
        """
        with Session() as s:
            s.add(self)
            s.commit()
            return

    def __str__(self):
        return f"<Task({int(self.task_is_regular)}) {self.task_target}<{self.task_when}>: [{self.task_args}]>"

    def __repr__(self):
        return f"<Task({int(self.task_is_regular)}) {self.task_target}<{self.task_when}>: [{self.task_args}]>"


class Notes(Base):
    __tablename__ = 'notes'

    note_id: Mapped[int] = mapped_column(primary_key=True)
    note_author: Mapped[int]
    note_text: Mapped[str]
    expires_in: Mapped[datetime]
    is_active: Mapped[bool]

    def __init__(self, author: int, text: str, expires: datetime = datetime.utcnow() + timedelta(hours=168+3),
                 active: bool = True):
        self.note_author = author
        self.note_text = text
        self.expires_in = expires
        self.is_active = active
        return

    def create(self):
        with Session() as s:
            s.add(self)
            s.commit()

    def restore(self):
        self.is_active = True
        self.expires_in = datetime.utcnow() + timedelta(hours=168+3)
        self.create()
        return

    def remove(self):
        self.is_active = False
        with Session() as s:
            s.add(self)
            s.commit()
        return

    def __str__(self):
        return f"<Note({int(self.note_author)}): {self.note_text[:20] + '...' if len(self.note_text) > 20 else ''}<{self.expires_in}]>"

    def __repr__(self):
        return f"<Note({int(self.note_author)}): {self.note_text[:20] + '...' if len(self.note_text) > 20 else ''}<{self.expires_in}]>"
