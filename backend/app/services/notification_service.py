from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User

def create_notification(
    db: Session,
    recipient_id: str,
    title: str,
    message: str,
    notification_type: str = "GENERAL",
    reference_id: Optional[str] = None
) -> Notification:
    notification = Notification(
        recipient_id=recipient_id,
        title=title,
        message=message,
        notification_type=notification_type,
        reference_id=reference_id
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def get_user_notifications(db: Session, user_id: str, limit: int = 50) -> List[Notification]:
    return db.query(Notification).filter(
        Notification.recipient_id == user_id
    ).order_by(Notification.created_at.desc()).limit(limit).all()

def get_unread_notification_count(db: Session, user_id: str) -> int:
    return db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.is_read == False
    ).count()

def mark_notification_as_read(db: Session, notification_id: str, user_id: str) -> bool:
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == user_id
    ).first()
    if notification:
        notification.is_read = True
        db.commit()
        return True
    return False

def mark_all_notifications_as_read(db: Session, user_id: str) -> int:
    notifications = db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.is_read == False
    ).all()
    count = 0
    for notif in notifications:
        notif.is_read = True
        count += 1
    db.commit()
    return count
