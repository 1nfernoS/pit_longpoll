from datetime import datetime
from typing import List, Dict

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ORM import Base, session

__all__ = ["Item", "Role", "UserStats", "UserInfo", "Equipment"]


class Item(Base):
    __tablename__ = 'item'

    item_id: Mapped[int] = mapped_column(primary_key=True)
    item_name: Mapped[str]
    item_has_price: Mapped[bool]

    item_users: Mapped[List["UserInfo"]] = relationship(secondary='equipment', back_populates='user_items',
                                                        viewonly=True)

    def __init__(self, item_id: int, name: str, has_price: bool = False):
        super().__init__()
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

    role_id: Mapped[int] = mapped_column(primary_key=True)
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
    role_can_take_money: Mapped[int]
    role_can_take_books: Mapped[int]
    role_can_take_ingredients: Mapped[int]

    role_users: Mapped[List["UserInfo"]] = relationship(back_populates='user_role', viewonly=True)

    def __init__(self, role_id: int, name: str, can_basic: bool = False, can_get_buff: bool = False,
                 can_check_stats: bool = False, can_balance: bool = False, can_profile_app_check: bool = False,
                 can_change_balance: bool = False, can_moderate: bool = False, can_kick: bool = False,
                 can_check_all_balance: bool = False, can_withdraw_bill: bool = False, can_change_role: bool = False,
                 can_utils: bool = False, can_take_money: bool = False, can_take_books: bool = False,
                 can_take_ingredients: bool = False):
        super().__init__()
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
        self.role_can_take_money = int(can_take_money)
        self.role_can_take_books = int(can_take_books)
        self.role_can_take_ingredients = int(can_take_ingredients)
        return

    def role_level_access(self) -> int:
        return int(f"{self.role_can_basic}{self.role_can_get_buff}{self.role_can_check_stats}{self.role_can_balance}"
                   f"{self.role_can_profile_app_check}{self.role_can_change_balance}{self.role_can_moderate}"
                   f"{self.role_can_kick}{self.role_can_check_all_balance}{self.role_can_withdraw_bill}"
                   f"{self.role_can_change_role}{self.role_can_utils}{self.role_can_take_money}"
                   f"{self.role_can_take_books}{self.role_can_take_ingredients}", 2)

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
            'role_can_utils': self.role_can_utils,
            'role_can_take_money': self.role_can_take_money,
            'role_can_take_books': self.role_can_take_books,
            'role_can_take_ingredients': self.role_can_take_ingredients
        }

    def bin_access(self) -> str:
        return bin(self.role_level_access())[2:]

    @staticmethod
    def get_guild_roles() -> List["Role"]:
        guild_roles = ['creator', 'leader',
                       'paymaster', 'librarian',
                       'captain', 'officer',
                       'guild_member']
        with session() as s:
            return s.query(Role).filter(Role.role_name.in_(guild_roles)).all()

    @staticmethod
    def leader_role() -> "Role":
        with session() as s:
            return s.query(Role).filter(Role.role_name == 'leader').first()

    @staticmethod
    def captain_role() -> "Role":
        with session() as s:
            return s.query(Role).filter(Role.role_name == 'captain').first()

    @staticmethod
    def officer_role() -> "Role":
        with session() as s:
            return s.query(Role).filter(Role.role_name == 'officer').first()

    @staticmethod
    def guild_role() -> "Role":
        with session() as s:
            return s.query(Role).filter(Role.role_name == 'guild_member').first()

    @staticmethod
    def newbie_role() -> "Role":
        with session() as s:
            return s.query(Role).filter(Role.role_name == 'guild_newbie').first()

    @staticmethod
    def guest_role() -> "Role":
        with session() as s:
            return s.query(Role).filter(Role.role_name == 'guild_guests').first()

    @staticmethod
    def other_role() -> "Role":
        with session() as s:
            return s.query(Role).filter(Role.role_name == 'others').first()

    @staticmethod
    def ban_role() -> "Role":
        with session() as s:
            return s.query(Role).filter(Role.role_name == 'blacklist').first()

    def __eq__(self, other: "Role"):
        if type(other) != Role:
            return False
        return self.role_id == other.role_id

    def __str__(self):
        return f"<Role {self.role_id}: {self.role_name} ({self.bin_access()})>"

    def __repr__(self):
        return f"<Role {self.role_id}: {self.role_name} ({self.bin_access()})>"


class UserStats(Base):
    __tablename__ = 'user_stats'

    user_id: Mapped[int] = mapped_column(ForeignKey('user_info.user_id'), primary_key=True)
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

    user_info: Mapped['UserInfo'] = relationship(back_populates='user_stats', viewonly=True)

    def __init__(self, user_id: int, class_id: int = None, level: int = 1,
                 attack: int = 5, defence: int = 5, strength: int = 5, agility: int = 5, endurance: int = 5,
                 luck: int = 1, accuracy: int = 1, concentration: int = 1,
                 last_update: datetime = datetime.now()):
        super().__init__()
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

    user_id: Mapped[int] = mapped_column(primary_key=True)
    user_profile_key: Mapped[str]
    role_id: Mapped[int] = mapped_column(ForeignKey('role.role_id'))
    balance: Mapped[int]
    elites_count: Mapped[int]
    siege_flag: Mapped[bool]

    user_items: Mapped[List["Item"]] = relationship(secondary='equipment', back_populates='item_users')
    user_stats: Mapped["UserStats"] = relationship(back_populates='user_info')
    user_role: Mapped["Role"] = relationship(back_populates='role_users', viewonly=True)

    def __init__(self, user_id: int, profile_key: str = None, role_id: int = 8, balance: int = 0, elites_count: int = 0,
                 siege_flag: bool = False):
        super().__init__()
        self.user_id = user_id
        self.user_profile_key = profile_key
        self.role_id = role_id
        self.balance = balance
        self.elites_count = elites_count
        self.siege_flag = siege_flag
        return

    def __repr__(self):
        return f'<UserInfo {self.user_id} ({self.role_id})>'

    def __str__(self):
        return f'<UserInfo {self.user_id} ({self.role_id})>'


class Equipment(Base):
    __tablename__ = 'equipment'

    user_id: Mapped[int] = mapped_column(ForeignKey(UserInfo.user_id), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey(Item.item_id), primary_key=True)
