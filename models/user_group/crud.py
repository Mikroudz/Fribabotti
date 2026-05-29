from typing import List
from sqlmodel import Session, select, exists, and_
from pydantic import ValidationError
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from .model import UserGroup, UpdateUserGroup, UserGroupRead
from models.user.model import User
from models.game_session.model import GameSession, GameSessionReadShortWithCourse
from models.course.model import Course


from models.links.user_group_members_link import UserGroupMembersLink
from models.links.session_participants_link import SessionParticipantsLink
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
        .where(
            UserGroupMembersLink.user_id == user_id,
            UserGroup.deleted == False,
        )
    )
    groups = session.exec(stmt).all()
    return groups


def read_group(session: Session, group_id: int) -> UserGroup:

    return session.get(UserGroup, group_id)


def read_group_invite(session: Session, invite: str) -> UserGroup:
    stmt = select(UserGroup).where(
        UserGroup.invite_code == invite, UserGroup.deleted == False
    )
    res = session.exec(stmt).first()
    return res


def read_group_long(session: Session, group_id: int, user_id: int) -> UserGroupRead:
    stmt = (
        select(UserGroup)
        .options(selectinload(UserGroup.members))
        .join(UserGroupMembersLink, UserGroup.id == UserGroupMembersLink.user_group_id)
        .where(
            UserGroupMembersLink.user_id == user_id,
            UserGroup.id == group_id,
            UserGroup.deleted == False,
        )
    )
    group = session.exec(stmt).first()
    if not group:
        raise HTTPException(
            status_code=404,
            detail="Group not found",
        )
    stmt_gamesessions = (
        select(GameSession, Course.name)
        # I dont really need to use users table for this but dunno how to access only the link user_id value
        .options(selectinload(GameSession.participants).load_only(User.id))
        .join(Course, GameSession.course_id == Course.id)
        .where(
            GameSession.user_group_id == group_id,
            UserGroup.deleted == False,
        )
        .order_by(GameSession.started_at.desc())
        .limit(5)
    )

    gamesessions = session.exec(stmt_gamesessions).all()

    return UserGroupRead(
        **group.model_dump(),
        recent_games=[
            GameSessionReadShortWithCourse(
                **game.model_dump(),
                course_name=course_name,
                participants=[p.id for p in game.participants],
            )
            for game, course_name in gamesessions
        ],
        members=group.members,
    )


def read_group_members(session: Session, group_id: int) -> List[User]:
    group = session.get(UserGroup, group_id)
    return group.members
