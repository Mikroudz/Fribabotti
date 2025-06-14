from typing import List
from sqlmodel import Session, select
from pydantic import ValidationError

from .model import UserGroup
from models.user.model import User

from models.links.user_group_members_link import UserGroupMembersLink


def create_group(session: Session, group_name: str, user_id: int) -> UserGroup:

    db_user = session.get(User, user_id)
    if db_user:
        try:
            group = UserGroup(name=group_name, members=[db_user])
        except ValidationError as e:
            raise e
        session.add(group)
        session.commit()
        session.refresh(group)

        return group


def edit_group(session: Session, group_name: str, group_id: int) -> UserGroup:

    db_group = session.get(UserGroup, group_id)
    if db_group:
        try:
            new_group = UserGroup(name=group_name)
            db_group.sqlmodel_update(new_group.model_dump(exclude_unset=True))
        except ValidationError as e:
            raise e
        session.commit()
        session.refresh(db_group)

    return db_group


def delete_group(session: Session, group_id: int):
    db_group = session.get(UserGroup, group_id)
    if db_group:
        setattr(db_group, "deleted", True)
        session.commit()


def read_groups(session: Session, user_id: int) -> List[UserGroup]:
    stmt = (
        select(UserGroup)
        .join(UserGroupMembersLink, UserGroup.id == UserGroupMembersLink.user_group_id)
        .where(UserGroupMembersLink.user_id == user_id)
    )
    groups = session.exec(stmt).all()
    return groups


def read_group(session: Session, group_id: int) -> UserGroup:

    return session.get(UserGroup, group_id)


def read_group_members(session: Session, group_id: int) -> List[User]:
    group = session.get(UserGroup, group_id)
    return group.members
