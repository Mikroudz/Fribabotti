from typing import List, Tuple
from sqlmodel import Session, select, and_, asc, desc, func

from fastapi import HTTPException, status

from .model import DeviceSession


def read_device_sessions_user(session: Session, user_id: int) -> List[DeviceSession]:

    stmt = select(DeviceSession).where(DeviceSession.user_id == user_id)
    res = session.exec(stmt).all()
    return res


def create_device_session(session: Session, device_id: int, user_id: int):
    if not device_id:
        # Device id required
        return None
    dev_session = DeviceSession(device_id_code=device_id, user_id=user_id)
    session.add(dev_session)
    session.commit()
    session.refresh(dev_session)
    return dev_session


def register_device_session_by_dev_id(
    session: Session, device_id: int
) -> DeviceSession | None:
    stmt = select(DeviceSession).where(DeviceSession.device_id_code == device_id)
    res = session.exec(stmt).first()
    if not res:
        raise HTTPException(404, "No session found")
    setattr(res, "has_identified", True)
    session.add(res)
    session.commit()
    session.refresh(res)
    return res


def delete_unidentified_device_sessions(session: Session, user_id: int):
    """Deletes all device sessions for a user that haven't been identified yet."""
    stmt = select(DeviceSession).where(
        and_(DeviceSession.user_id == user_id, DeviceSession.has_identified == False)
    )
    unidentified_sessions = session.exec(stmt).all()

    for dev_session in unidentified_sessions:
        session.delete(dev_session)

    session.commit()


def get_user_id_from_device(
    session: Session,
    token: str,
) -> int:
    """
    Validates the device token (DeviceSession ID) and returns the associated user_id.
    """
    # Look up the device session by its ID and ensure it is fully paired
    stmt = select(DeviceSession).where(
        DeviceSession.id == token, DeviceSession.has_identified == True
    )
    device_session = session.exec(stmt).first()

    # If no session is found, or it's not tied to a user, reject the request
    if not device_session or not device_session.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or unverified device token.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return device_session.user_id
