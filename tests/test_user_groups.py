import pytest
from sqlmodel import select, Session

from models.user_group.model import UserGroup

from models.user_group.crud import (
    create_group,
    edit_group,
    invite_join_group,
    read_groups,
)
from models.user.crud import create_user
from models.links.user_group_members_link import UserGroupMembersLink


@pytest.fixture()
def setup_dummy_data(session: Session):
    user = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 1},
        )(),
    )
    return user


def test_create_user_group_success(session: Session, setup_dummy_data):
    user = setup_dummy_data
    g = create_group(session, "test", True, user.id)
    group = session.get(UserGroup, g.id)
    assert group.name == "test"
    assert len(group.invite_code) == 16
    assert group.notify_groups
    links = session.exec(
        select(UserGroupMembersLink).where(UserGroupMembersLink.user_group_id == g.id)
    ).all()
    assert len(links) == 1, "User is added to group members"
    groups = read_groups(session, user.id)
    assert len(groups) == 1


def test_update_user_group_success(session: Session, setup_dummy_data):
    user = setup_dummy_data
    g = create_group(session, "test", True, user.id)
    old_invite = g.invite_code
    edit_group(session, group_id=g.id, reset_invite=True, data=UserGroup(name="a"))
    group = session.get(UserGroup, g.id)
    assert group.name == "a"
    assert old_invite != group.invite_code


def test_update_user_group_dont_change_invite_success(
    session: Session, setup_dummy_data
):
    user = setup_dummy_data
    g = create_group(session, "test", True, user.id)
    old_invite = g.invite_code
    edit_group(session, group_id=g.id, reset_invite=False, data=UserGroup(name="a"))

    group = session.get(UserGroup, g.id)
    assert group.name == "a"
    assert old_invite == group.invite_code


def test_join_group_invite_success(session: Session, setup_dummy_data):
    user = setup_dummy_data
    g = create_group(session, "test", True, user.id)
    user2 = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 2},
        )(),
    )
    invite_join_group(session, g.invite_code, user2.id)
    links = session.exec(
        select(UserGroupMembersLink).where(UserGroupMembersLink.user_group_id == g.id)
    ).all()
    assert len(links) == 2


def test_join_group_invite_join_twice(session: Session, setup_dummy_data):
    user = setup_dummy_data
    g = create_group(session, "test", True, user.id)

    invite_join_group(session, g.invite_code, user.id)
    links = session.exec(
        select(UserGroupMembersLink).where(UserGroupMembersLink.user_group_id == g.id)
    ).all()
    assert len(links) == 1


def test_join_group_invite_failure_user_does_not_exist(
    session: Session, setup_dummy_data
):
    user = setup_dummy_data
    g = create_group(session, "test", True, user.id)

    invite_ret = invite_join_group(session, g.invite_code, 2)

    assert invite_ret == None
    g = session.get(UserGroup, g.id)
    links = session.exec(
        select(UserGroupMembersLink).where(UserGroupMembersLink.user_group_id == g.id)
    ).all()
    assert len(links) == 1, "User is not added to the members"


def test_join_group_invite_failure_incorrect_invite_code(
    session: Session, setup_dummy_data
):
    user = setup_dummy_data
    g = create_group(session, "test", True, user.id)
    user2 = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 2},
        )(),
    )
    invite_ret = invite_join_group(session, "asdasdasd", user2.id)

    assert invite_ret == None
    links = session.exec(
        select(UserGroupMembersLink).where(UserGroupMembersLink.user_group_id == g.id)
    ).all()
    assert len(links) == 1, "User is not added to the members"
