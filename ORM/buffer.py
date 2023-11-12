from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ORM import Base

__all__ = ["BuffType", "BuffTypeCmd", "BuffCmd", "BuffUser"]


class BuffType(Base):
    __tablename__ = 'buff_type'

    buff_type_id: Mapped[int] = mapped_column(primary_key=True)
    buff_type_name: Mapped[str]

    buff_users: Mapped[List["BuffUser"]] = relationship(back_populates='buff_user_type')
    buff_commands: Mapped[List["BuffCmd"]] = relationship(secondary='buff_type_cmd', back_populates='buff_cmd_type')

    def __init__(self, type_id: int, type_name: str):
        super().__init__()
        self.buff_type_id = type_id
        self.buff_type_name = type_name
        return

    def __str__(self):
        return f"<BuffType {self.buff_type_id}: {self.buff_type_name}>"

    def __repr__(self):
        return f"<BuffType {self.buff_type_id}: {self.buff_type_name}>"


class BuffCmd(Base):
    __tablename__ = 'buff_cmd'

    buff_cmd_id: Mapped[int] = mapped_column(primary_key=True)
    buff_cmd_text: Mapped[str]

    buff_cmd_type: Mapped[BuffType] = relationship(secondary='buff_type_cmd', back_populates='buff_commands',
                                                   viewonly=True)

    def __init__(self, cmd_id: int, cmd_text: str):
        super().__init__()
        self.buff_cmd_id = cmd_id
        self.buff_cmd_text = cmd_text
        return

    def __str__(self):
        return f"<BuffCmd {self.buff_cmd_id}: {self.buff_cmd_text}>"

    def __repr__(self):
        return f"<BuffCmd {self.buff_cmd_id}: {self.buff_cmd_text}>"


class BuffTypeCmd(Base):
    __tablename__ = 'buff_type_cmd'

    buff_type_id: Mapped[int] = mapped_column(ForeignKey(BuffType.buff_type_id), primary_key=True)
    buff_cmd_id: Mapped[int] = mapped_column(ForeignKey(BuffCmd.buff_cmd_id), primary_key=True)


class BuffUser(Base):
    __tablename__ = 'buff_user'

    buff_user_id: Mapped[int] = mapped_column(primary_key=True)
    buff_user_is_active: Mapped[bool]
    buff_user_profile_key: Mapped[str]
    buff_user_token: Mapped[str]
    buff_type_id: Mapped[int] = mapped_column(ForeignKey(BuffType.buff_type_id))
    buff_user_race1: Mapped[int]
    buff_user_race2: Mapped[int]
    buff_user_chat_id: Mapped[int]

    buff_user_type: Mapped[BuffType] = relationship(back_populates='buff_users', viewonly=True)

    def __init__(self, user_id: int, is_active: bool, profile_key: str, token: str,
                 type_id: int, race1: int, race2: int, chat_id: int):
        super().__init__()
        self.buff_user_id = user_id
        self.buff_user_is_active = is_active
        self.buff_user_profile_key = profile_key
        self.buff_user_token = token
        self.buff_type_id = type_id
        self.buff_user_race1 = race1
        self.buff_user_race2 = race2
        self.buff_user_chat_id = chat_id
        return

    def __str__(self):
        return f"<BuffUser {self.buff_user_id}: {self.buff_type_id}>"

    def __repr__(self):
        return f"<BuffUser {self.buff_user_id}: {self.buff_type_id}>"
