import pytest
from sqlmodel import select, Session


from models.course.crud import create_course

from models.game.crud import create_game

from models.track.crud import upsert_track, delete_track

from models.game_session.crud import (
    create_game_session,
    end_game_session,
    delete_game_session,
    join_game_session,
    read_game_session_user_groups,
    read_game_session_user,
)
from models.game_session.model import GameSession

from models.user.crud import create_user

from models.user_group.model import UserGroup
from models.user_group.crud import invite_join_group

from models.score.crud import upsert_score, read_scores, read_users_scores
from models.score.model import Score

from models.links.session_participants_link import SessionParticipantsLink
from models.links.user_group_members_link import UserGroupMembersLink


course_location = "hervanta"
course_name = "hervannan frisbeegolf"


@pytest.fixture()
def setup_dummy_data(session: Session):
    game = create_game(session, "testipeli")

    course = create_course(session, course_name, course_location, game.id)
    user = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 1},
        )(),
    )
    user_group = UserGroup(name="testi", members=[user])
    session.add(user_group)
    session.commit()
    session.refresh(user_group)

    track = upsert_track(session, 1, 2, course.id)

    return game, course, user, user_group, track


def test_create_end_game_session_success(session: Session, setup_dummy_data):
    game, course, user, user_group, _ = setup_dummy_data
    create_game_session(session, user.id, course.id, user_group.id)
    db_sessions = session.exec(select(GameSession)).all()
    assert len(db_sessions) == 1
    assert db_sessions[0].ended_at == None

    end_game_session(session, db_sessions[0].id)
    db_sessions = session.exec(select(GameSession)).all()
    assert len(db_sessions) == 1
    assert db_sessions[0].ended_at > db_sessions[0].started_at
    assert db_sessions[0].ended_at_local("Europe/Helsinki", False) > db_sessions[
        0
    ].started_at_local("Europe/Helsinki", False)


def test_delete_game_session(session: Session, setup_dummy_data):
    game, course, user, user_group, _ = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)
    delete_game_session(session, game_session.id)
    db_sessions = session.exec(select(GameSession)).all()
    assert len(db_sessions) == 0


def test_join_game_session(session: Session, setup_dummy_data):
    game, course, user, user_group, _ = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)
    user2 = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 2},
        )(),
    )

    join_game_session(session, user2.id, game_session.id)
    db_sessions = session.exec(select(GameSession)).all()
    assert len(db_sessions) == 1
    assert len(db_sessions[0].participants) == 2


def test_read_game_session_all_user_without_scores(session: Session, setup_dummy_data):
    game, course, user, user_group, _ = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)
    user2 = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 2},
        )(),
    )
    user3 = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 3},
        )(),
    )

    # Add user to session
    join_game_session(session, user2.id, game_session.id)
    db_scores = read_users_scores(session, game_session.id)
    assert len(db_scores) == 2, "Two users are in the session"
    assert [score for (user, score) in db_scores] == [
        0,
        0,
    ], "users have 0 score by default"


def test_read_game_session_scores_no_participants(session: Session, setup_dummy_data):
    game, course, user, user_group, _ = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)
    participant_link = session.exec(
        select(SessionParticipantsLink).where(
            SessionParticipantsLink.user_id == user.id
        )
    ).one()
    session.delete(participant_link)
    session.commit()
    db_scores = read_users_scores(session, game_session.id)
    assert len(db_scores) == 0


def test_read_game_session_all_user_with_scores(session: Session, setup_dummy_data):
    game, course, user, user_group, _ = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)
    user2 = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 2},
        )(),
    )
    # Add some tracks for scores
    upsert_track(session, 1, 3, course.id)
    upsert_track(session, 2, 3, course.id)
    # add scores for user 1
    upsert_score(session, 1, 1, user.id, game_session.id)
    upsert_score(session, 1, 2, user.id, game_session.id)

    # Add user to session
    join_game_session(session, user2.id, game_session.id)

    db_scores = read_users_scores(session, game_session.id)
    assert [score for (user, score) in db_scores if user.id == 1] == [
        2
    ], "User 1 shall have 2 as score (score is track par + saved)"
    assert [score for (user, score) in db_scores if user.id == 2] == [
        0
    ], "User 2 has no scores"


def test_get_game_session_same_group_not_joined(session: Session, setup_dummy_data):
    game, course, user, user_group, _ = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)
    user2 = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 3},
        )(),
    )

    db_sessions = read_game_session_user_groups(session, user2.id)
    assert (
        len(db_sessions) == 0
    ), "User does not see sessions from groups he is not joined"

    invite_join_group(session, user_group.invite_code, user2.id)

    db_games = read_game_session_user_groups(session, user2.id)
    assert len(db_games) == 1, "After joining group session is visible"
    db_active_sessions = read_game_session_user(session, user2.id)
    assert len(db_active_sessions) == 0, "Session not returned as active"


def test_read_game_session_user_joined_session(session: Session, setup_dummy_data):
    game, course, user, user_group, _ = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)
    user2 = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 3},
        )(),
    )
    invite_join_group(session, user_group.invite_code, user2.id)
    join_game_session(session, user2.id, game_session.id)

    db_games = read_game_session_user_groups(session, user2.id)
    assert len(db_games) == 0, "Session should not be visible in group sessions"
    db_active_sessions = read_game_session_user(session, user2.id)
    assert len(db_active_sessions) == 1, "Session is returned from active sessions"


def test_get_game_session_user_multiple_groups_game_sessions(
    session: Session, setup_dummy_data
):
    game, course, user, user_group, _ = setup_dummy_data
    group2 = UserGroup(name="testi2", members=[user])
    user2 = create_user(
        session,
        type(
            "User",
            (object,),
            {"first_name": "tsti", "username": "asd", "id": 3},
        )(),
    )
    session.add(group2)
    session.commit()
    session.refresh(group2)

    game_session1 = create_game_session(session, user.id, course.id, user_group.id)
    game_session2 = create_game_session(session, user.id, course.id, group2.id)

    invite_join_group(session, user_group.invite_code, user2.id)

    db_games = read_game_session_user_groups(session, user2.id)
    assert len(db_games) == 1, "After joining group session is visible"

    # Join second group with session
    invite_join_group(session, group2.invite_code, user2.id)
    db_games = read_game_session_user_groups(session, user2.id)
    assert len(db_games) == 2, "Two sessions visible"

    game_session3 = create_game_session(session, user.id, course.id, group2.id)
    # Created session visible
    db_games = read_game_session_user_groups(session, user2.id)
    assert len(db_games) == 3, "Three sessions visible"

    # End game session
    end_game_session(session, game_session1.id)
    db_games = read_game_session_user_groups(session, user2.id)
    assert len(db_games) == 2, "Two sessions visible after ending one"


def test_create_score_success(session: Session, setup_dummy_data):
    game, course, user, user_group, track = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)

    upsert_score(session, 1, track.track_number, user.id, game_session.id)
    db_scores = session.exec(select(Score)).all()
    assert len(db_scores) == 1
    assert db_scores[0].score == 1


def test_create_score_unique_another_session_success(
    session: Session, setup_dummy_data
):
    game, course, user, user_group, track = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)
    game_session2 = create_game_session(session, user.id, course.id, user_group.id)

    upsert_score(session, 1, track.track_number, user.id, game_session.id)
    upsert_score(session, 2, track.track_number, user.id, game_session2.id)
    session.refresh(game_session)
    session.refresh(game_session2)

    db_scores = session.exec(select(Score)).all()
    assert len(db_scores) == 2
    assert game_session2.scores[0].score == 2
    assert game_session.scores[0].score == 1


def test_create_score_failure_missing_linked_data(session: Session, setup_dummy_data):
    game, course, user, user_group, track = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)

    # missing track
    upsert_score(session, 1, 123, user.id, game_session.id)
    # missing user
    upsert_score(session, 1, track.track_number, 123, game_session.id)
    # missing session
    upsert_score(session, 1, track.track_number, user.id, 123)

    db_scores = session.exec(select(Score)).all()
    assert len(db_scores) == 0


def test_update_score_success(session: Session, setup_dummy_data):
    game, course, user, user_group, track = setup_dummy_data
    game_session = create_game_session(session, user.id, course.id, user_group.id)

    upsert_score(session, 1, track.track_number, user.id, game_session.id)
    upsert_score(session, 2, track.track_number, user.id, game_session.id)

    db_scores = session.exec(select(Score)).all()
    assert len(db_scores) == 1
    assert db_scores[0].score == 2


def test_read_scores_session(session: Session, setup_dummy_data):
    game, course, user, user_group, track = setup_dummy_data
    course2 = create_course(session, "somecourse", "ihasama", game.id)
    game_session = create_game_session(session, user.id, course.id, user_group.id)
    game_session2 = create_game_session(session, user.id, course2.id, user_group.id)

    for i in range(1, 11):
        upsert_track(session, i, 3, course.id)
        upsert_track(session, i, 3, course2.id)

    upsert_score(session, 1, 1, user.id, game_session.id)
    upsert_score(session, 2, 1, user.id, game_session2.id)

    scores = read_scores(session, game_session.id, user.id)
    assert len(scores) == 10, "Correct track count is returned"
    assert (
        len([score for score, track in scores if score != None]) == 1
    ), "One score recorded"
    assert (
        len(
            [
                score
                for score, track in scores
                if score
                and score.score == 1
                and score.track_number == 1
                and score.track_number == track.track_number
            ]
        )
        == 1
    ), "Score has correct track number and score"
    delete_track(session, 1, course.id)
    scores = read_scores(session, game_session.id, user.id)
    assert len(scores) == 9, "Correct track count is returned after deleting track"
    assert (
        len([score for score, track in scores if score != None]) == 0
    ), "Recorded score is not returned if track is deleted"
    # Add track back
    upsert_track(session, 1, 3, course.id)
    scores = read_scores(session, game_session.id, user.id)
    assert len(scores) == 10, "Correct track count is returned"
    assert (
        len([score for score, track in scores if score != None]) == 1
    ), "One score recorded"
