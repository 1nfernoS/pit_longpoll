from datetime import datetime
from typing import List, Dict, Type

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Mapped, Session, relationship

from config import db_data

__all__ = ['session', 'UserInfo', 'UserStats', 'Role', 'Item', 'BuffUser', 'BuffType', 'BuffCmd', 'Logs']

__data_source = f"{db_data['dialect']}+{db_data['connector']}://" \
              f"{db_data['user']}:{db_data['password']}@" \
              f"{db_data['host']}/{db_data['database']}"

__engine = create_engine(__data_source)

metadata = MetaData()
# metadata.reflect(engine)


Base = automap_base(metadata=metadata)


def session() -> Session:
    return Session(__engine)


class Item(Base):
    __tablename__ = 'item'

    item_id: Mapped[int]
    item_name: Mapped[str]
    item_has_price: Mapped[bool]

    item_users: Mapped[List["UserInfo"]] = relationship(secondary='equipment', back_populates='user_items',
                                                        viewonly=True)

    def __init__(self, item_id: int, name: str, has_price: bool = False):
        self.item_id = item_id
        self.item_name = name
        self.item_has_price = has_price
        return

    def __str__(self):
        return f'<Item {self.item_id}: {self.item_name}>'

    def __repr__(self):
        return f'<Item {self.item_id}: {self.item_name}>'


class Role(Base):
    __tablename__ = 'role'

    role_id: Mapped[int]
    role_name: Mapped[str]
    role_can_basic: Mapped[int]
    role_can_get_buff: Mapped[int]
    role_can_check_stats: Mapped[int]
    role_can_balance: Mapped[int]
    role_can_profile_app_check: Mapped[int]
    role_can_change_balance: Mapped[int]
    role_can_moderate: Mapped[int]
    role_can_kick: Mapped[int]
    role_can_check_all_balance: Mapped[int]
    role_can_withdraw_bill: Mapped[int]
    role_can_change_role: Mapped[int]
    role_can_utils: Mapped[int]

    role_users: Mapped[List["UserInfo"]] = relationship(viewonly=True)

    def __init__(self, role_id: int, name: str, can_basic: bool = False, can_get_buff: bool = False,
                 can_check_stats: bool = False, can_balance: bool = False, can_profile_app_check: bool = False,
                 can_change_balance: bool = False, can_moderate: bool = False, can_kick: bool = False,
                 can_check_all_balance: bool = False, can_withdraw_bill: bool = False, can_change_role: bool = False,
                 can_utils: bool = False):
        if role_id < 0:
            raise ValueError
        self.role_id = role_id
        self.role_name = name
        self.role_can_basic = int(can_basic)
        self.role_can_get_buff = int(can_get_buff)
        self.role_can_check_stats = int(can_check_stats)
        self.role_can_balance = int(can_balance)
        self.role_can_profile_app_check = int(can_profile_app_check)
        self.role_can_change_balance = int(can_change_balance)
        self.role_can_moderate = int(can_moderate)
        self.role_can_kick = int(can_kick)
        self.role_can_check_all_balance = int(can_check_all_balance)
        self.role_can_withdraw_bill = int(can_withdraw_bill)
        self.role_can_change_role = int(can_change_role)
        self.role_can_utils = int(can_utils)
        return

    def role_level_access(self) -> int:
        return int(f"{self.role_can_basic}{self.role_can_get_buff}{self.role_can_check_stats}{self.role_can_balance}"
                   f"{self.role_can_profile_app_check}{self.role_can_change_balance}{self.role_can_moderate}"
                   f"{self.role_can_kick}{self.role_can_check_all_balance}{self.role_can_withdraw_bill}"
                   f"{self.role_can_change_role}{self.role_can_utils}", 2)

    def dict_access(self) -> Dict[str, int]:
        return {
            'role_can_basic': self.role_can_basic,
            'role_can_get_buff': self.role_can_get_buff,
            'role_can_check_stats': self.role_can_check_stats,
            'role_can_balance': self.role_can_balance,
            'role_can_profile_app_check': self.role_can_profile_app_check,
            'role_can_change_balance': self.role_can_change_balance,
            'role_can_moderate': self.role_can_moderate,
            'role_can_kick': self.role_can_kick,
            'role_can_check_all_balance': self.role_can_check_all_balance,
            'role_can_withdraw_bill': self.role_can_withdraw_bill,
            'role_can_change_role': self.role_can_change_role,
            'role_can_utils': self.role_can_utils
        }

    def bin_access(self) -> str:
        return bin(self.role_level_access())[2:]

    def __str__(self):
        return f"<Role {self.role_id}: {self.role_name} ({self.bin_access()})>"

    def __repr__(self):
        return f"<Role {self.role_id}: {self.role_name} ({self.bin_access()})>"


class UserStats(Base):
    __tablename__ = 'user_stats'

    user_id: Mapped[int]
    class_id: Mapped[int]
    user_level: Mapped[int]
    user_attack: Mapped[int]
    user_defence: Mapped[int]
    user_strength: Mapped[int]
    user_agility: Mapped[int]
    user_endurance: Mapped[int]
    user_luck: Mapped[int]
    user_accuracy: Mapped[int]
    user_concentration: Mapped[int]
    last_update: Mapped[datetime]

    user_info: Mapped['UserInfo'] = relationship(viewonly=True, back_populates='user_stats')

    def __init__(self, user_id: int, class_id: int = None, level: int = 1,
                 attack: int = 5, defence: int = 5, strength: int = 5, agility: int = 5, endurance: int = 5,
                 luck: int = 1, accuracy: int = 1, concentration: int = 1,
                 last_update: datetime = datetime.now()):
        self.user_id = user_id
        self.class_id = class_id
        self.user_level = level
        self.user_attack = attack
        self.user_defence = defence
        self.user_strength = strength
        self.user_agility = agility
        self.user_endurance = endurance
        self.user_luck = luck
        self.user_accuracy = accuracy
        self.user_concentration = concentration
        self.last_update = last_update
        return

    def __str__(self):
        return f'<UserStats {self.user_id} ({self.last_update})>'

    def __repr__(self):
        return f'<UserStats {self.user_id} ({self.last_update})>'

    def get_stats(self):
        return {
            'user_id': self.user_id,
            'class_id': self.class_id,
            'user_level': self.user_level,
            'user_attack': self.user_attack,
            'user_defence': self.user_defence,
            'user_strength': self.user_strength,
            'user_agility': self.user_agility,
            'user_endurance': self.user_endurance,
            'user_luck': self.user_luck,
            'user_accuracy': self.user_accuracy,
            'user_concentration': self.user_concentration,
            'last_update': self.last_update
        }


class UserInfo(Base):
    __tablename__ = 'user_info'

    user_id: Mapped[int]
    user_profile_key: Mapped[str]
    role_id: Mapped[int]
    balance: Mapped[int]

    user_items: Mapped[List["Item"]] = relationship(secondary='equipment', back_populates='item_users',
                                                    overlaps="item_collection,userinfo_collection")
    user_stats: Mapped["UserStats"] = relationship(back_populates='user_info', overlaps='userinfo,userstats_collection')

    user_role: Mapped["Role"] = relationship(back_populates='role_users', viewonly=True)

    def __init__(self, user_id: int, profile_key: str = None, role_id: int = 8, balance: int = 0):
        self.user_id = user_id
        self.user_profile_key = profile_key
        self.role_id = role_id
        self.balance = balance
        return

    def __repr__(self):
        return f'<UserInfo {self.user_id} ({self.role_id})>'

    def __str__(self):
        return f'<UserInfo {self.user_id} ({self.role_id})>'


class BuffType(Base):
    __tablename__ = 'buff_type'

    buff_type_id: Mapped[int]
    buff_type_name: Mapped[str]

    buff_users: Mapped[List["BuffUser"]] = relationship(back_populates='buff_user_type',
                                                        overlaps='buffuser_collection,bufftype')
    buff_commands: Mapped[List["BuffCmd"]] = relationship(secondary='buff_type_cmd', back_populates='buff_cmd_type',
                                                          overlaps='buffcmd_collection,bufftype_collection')

    def __init__(self, type_id: int, type_name: str):
        self.buff_type_id = type_id
        self.buff_type_name = type_name
        return

    def __str__(self):
        return f"<BuffType {self.buff_type_id}: {self.buff_type_name}>"

    def __repr__(self):
        return f"<BuffType {self.buff_type_id}: {self.buff_type_name}>"


class BuffCmd(Base):
    __tablename__ = 'buff_cmd'

    buff_cmd_id: Mapped[int]
    buff_cmd_text: Mapped[str]

    buff_cmd_type: Mapped[BuffType] = relationship(secondary='buff_type_cmd', back_populates='buff_commands',
                                                   viewonly=True, overlaps='bufftype_collection')

    def __init__(self, cmd_id: int, cmd_text: str):
        self.buff_cmd_id = cmd_id
        self.buff_cmd_text = cmd_text
        return

    def __str__(self):
        return f"<BuffCmd {self.buff_cmd_id}: {self.buff_cmd_text}>"

    def __repr__(self):
        return f"<BuffCmd {self.buff_cmd_id}: {self.buff_cmd_text}>"


class BuffUser(Base):
    __tablename__ = 'buff_user'

    buff_user_id: Mapped[int]
    buff_user_is_active: Mapped[bool]
    buff_user_profile_key: Mapped[str]
    buff_user_token: Mapped[str]
    buff_type_id: Mapped[int]
    buff_user_race1: Mapped[int]
    buff_user_race2: Mapped[int]
    buff_user_chat_id: Mapped[int]

    buff_user_type: Mapped[BuffType] = relationship(back_populates='buff_users', overlaps="bufftype", viewonly=True)

    def __init__(self, user_id: int, is_active: bool, profile_key: str, token: str,
                 type_id: int, race1: int, race2: int, chat_id: int):
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


class Logs(Base):
    __tablename__ = 'logs'

    logs_entry_id: Mapped[int]
    logs_timestamp: Mapped[datetime]
    logs_user_id: Mapped[int]
    logs_action: Mapped[str]
    logs_on_user_id: Mapped[int]
    logs_reason: Mapped[str]
    logs_on_message: Mapped[str]

    def __init__(self, user_id: int, action: str, reason: str = None,
                 on_message: str = None, on_user_id: int = None):
        self.logs_timestamp = datetime.now()
        self.logs_user_id = user_id
        self.logs_action = action
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


metadata.reflect(__engine, extend_existing=True)
Base.prepare()

tables = (UserInfo, UserStats, Item, Role, BuffUser, BuffCmd, BuffType)
# connection = engine.connect()

if __name__ == '__main__':

    # search = 'удар'
    # items: List[Type[Item]] = session().query(Item)\
    #     .filter(Item.item_name.op('regexp')(f"(Книга - |Книга - [[:alnum:]]+ |^[[:alnum:]]+ |^){search}.*$")).all()
    # print([str(i) for i in items])
    # me: UserInfo = session.query(UserInfo).filter(UserInfo.user_id == 158154503).first()
    # it: Item = session.query(Item).filter(Item.item_id == 13650).first()
    # equip: List[Item] = me.user_items
    # print(me.user_items)
    # me.user_items.append(it)
    # print(me.user_items)
    # session.add(me)
    # session.commit()
    #
    # me: UserInfo = session.query(UserInfo).filter(UserInfo.user_id == 158154503).first()
    # print(me.user_items)
    #
    # me.user_items.remove(it)
    # print(me.user_items)
    # session.add(me)
    # session.commit()
    #
    # me: UserInfo = session.query(UserInfo).filter(UserInfo.user_id == 158154503).first()
    # print(me.user_items)

    pass
