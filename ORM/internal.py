from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from ORM import Base, session


__all__ = ["LogsType", "Logs"]

class LogsType(Base):

    __tablename__ = 'logs_type'

    logs_type_id: Mapped[int] = mapped_column(primary_key=True)
    logs_type_name: Mapped[str]

    def __init__(self, name: str):
        super().__init__()
        self.logs_type_name = name
        return

    def register(self):
        with session() as s:
            s.add(self)
            s.commit()
        return

    def __str__(self):
        return f"<LogsType {self.logs_type_id}: {self.logs_type_name}>"

    def __repr__(self):
        return f"<LogsType {self.logs_type_id}: {self.logs_type_name}>"


class Logs(Base):
    __tablename__ = 'logs'

    logs_entry_id: Mapped[int] = mapped_column(primary_key=True)
    logs_timestamp: Mapped[datetime]
    logs_user_id: Mapped[int]
    logs_action: Mapped[int]
    logs_on_user_id: Mapped[int]
    logs_reason: Mapped[str]
    logs_on_message: Mapped[str]

    def __init__(self, user_id: int, action: str, reason: str = None,
                 on_message: str = None, on_user_id: int = None):
        super().__init__()

        with session() as s:
            type_id: LogsType = s.query(LogsType).filter(LogsType.logs_type_name == action).first()
        if not type_id:
            LogsType(action).register()
            s = session()
            type_id: LogsType = s.query(LogsType).filter(LogsType.logs_type_name == action).first()
            s.close()

        self.logs_timestamp = datetime.now()
        self.logs_user_id = user_id
        self.logs_action = type_id.logs_type_id
        self.logs_on_user_id = on_user_id
        self.logs_reason = reason
        self.logs_on_message = on_message
        return

    def make_record(self):
        with session() as s:
            s.add(self)
            s.commit()
        return

    def __str__(self):
        return f"<Logs {self.logs_user_id}: {self.logs_action}>"

    def __repr__(self):
        return f"<Logs {self.logs_user_id}: {self.logs_action}>"
