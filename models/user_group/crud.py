from typing import List
from sqlmodel import Session, select, exists, and_
from pydantic import ValidationError

from .model import UserGroup, UpdateUserGroup
from models.user.model import User

from models.links.user_group_members_link import UserGroupMembersLink
import logging

logger = logging.getLogger(__name__)


def create_group(
    session: Session, group_name: str, notify_groups: bool, user_id: int
) -> UserGroup:

    db_user = session.get(User, user_id)
    if db_user:
        try:
            group = UserGroup(
                name=group_name, members=[db_user], notify_groups=notify_groups
            )
        except ValidationError as e:
            raise e

        session.add(group)
        session.commit()
        session.refresh(group)

        return group


def edit_group(
    session: Session,
    group_id: int,
    data: UpdateUserGroup = UpdateUserGroup(),
    reset_invite: bool = False,
) -> UserGroup:

    db_group = session.get(UserGroup, group_id)
    if db_group:
        try:
            if reset_invite:
                db_group.reset_invite()
            db_group.sqlmodel_update(data.model_dump(exclude_unset=True))
        except ValidationError as e:
            raise e
        session.commit()
        session.refresh(db_group)

    return db_group


def check_user_group_membership(session: Session, group_id: int, user_id: int) -> bool:
    db_member = session.exec(
        select(UserGroupMembersLink).where(
            and_(
                UserGroupMembersLink.user_group_id == group_id,
                UserGroupMembersLink.user_id == user_id,
            )
        )
    ).first()
    return bool(db_member)


def invite_join_group(
    session: Session, group_invite: str, user_id: int
) -> UserGroup | None:

    stmt = select(UserGroup).where(UserGroup.invite_code == group_invite)
    db_group = session.exec(stmt).first()
    if db_group and not check_user_group_membership(session, db_group.id, user_id):
        # Do we have user
        user = session.get(User, user_id)
        if user:
            member = UserGroupMembersLink(user_group_id=db_group.id, user_id=user_id)
            session.add(member)
            session.commit()
        else:
            return None

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
