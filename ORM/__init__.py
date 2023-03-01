from datetime import datetime
from typing import List, ClassVar, Optional, Dict, Type

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Mapped, Session, relationship

from config import db_data

data_source = f"{db_data['dialect']}+{db_data['connector']}://" \
              f"{db_data['user']}:{db_data['password']}@" \
              f"{db_data['host']}/{db_data['database']}"

engine = create_engine(data_source)

metadata = MetaData()
# metadata.reflect(engine)


Base = automap_base(metadata=metadata)


class Item(Base):
    __tablename__ = 'item'

    item_id: Mapped[int]
    item_name: Mapped[str]
    item_has_price: Mapped[bool]
    item_users: Mapped[List["UserInfo"]] = relationship(secondary='equipment', back_populates='user_items',
                                                        viewonly=True)

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

    def __str__(self):
        return f"<BuffUser {self.buff_user_id}: {self.buff_type_id}>"

    def __repr__(self):
        return f"<BuffUser {self.buff_user_id}: {self.buff_type_id}>"


metadata.reflect(engine, extend_existing=True)
Base.prepare()

session = Session(engine)
connection = engine.connect()

if __name__ == '__main__':

    search = 'удар'
    items: List[Type[Item]] = session.query(Item)\
        .filter(Item.item_name.op('regexp')(f"(Книга - |Книга - [[:alnum:]]+ |^[[:alnum:]]+ |^){search}.*$")).all()
    # print([str(i) for i in items])
    me: UserInfo = session.query(UserInfo).filter(UserInfo.user_id == 158154503).first()
    it: Item = session.query(Item).filter(Item.item_id == 13650).first()
    equip: List[Item] = me.user_items
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
