from sqlalchemy.orm import Session
from app.models.notification import Notification


from app.utils.websocket_manager import manager
import asyncio

class NotificationService_:

    def create(
        self, db: Session,
        user_id: int,
        title: str,
        message: str,
        type: str,
        link: str = None
    ):
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            link=link
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        # Push live via WebSocket if user is connected
        try:
            asyncio.create_task(manager.send_to_user(user_id, {
                "type": "notification",
                "data": {
                    "id": notif.id,
                    "title": notif.title,
                    "message": notif.message,
                    "notif_type": notif.type,
                    "link": notif.link,
                    "created_at": notif.created_at.isoformat()
                }
            }))
        except Exception:
            pass  # WebSocket push failing shouldn't break the notification save

        return notif


    # ── GET MY NOTIFICATIONS ──
    def get_my_notifications(
        self, db: Session,
        user_id: int,
        unread_only: bool = False
    ):
        query = db.query(Notification).filter(
            Notification.user_id == user_id
        )

        if unread_only:
            query = query.filter(Notification.is_read == False)

        return query.order_by(
            Notification.created_at.desc()
        ).limit(50).all()


    # ── MARK AS READ ──
    def mark_read(
        self, db: Session,
        user_id: int,
        notification_id: int
    ):
        notif = db.query(Notification).filter(
            Notification.id      == notification_id,
            Notification.user_id == user_id
        ).first()

        if notif:
            notif.is_read = True
            db.commit()

        return {"message": "Marked as read"}


    # ── MARK ALL AS READ ──
    def mark_all_read(self, db: Session, user_id: int):
        db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        db.commit()
        return {"message": "All notifications marked as read"}


    # ── GET UNREAD COUNT ──
    def get_unread_count(self, db: Session, user_id: int):
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        return {"unread_count": count}


notification_service = NotificationService_()