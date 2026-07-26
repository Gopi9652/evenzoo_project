from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
import asyncio

from app.models.message import Message
from app.models.booking import Booking
from app.models.user import User
from app.models.vendor import VendorProfile
from app.schemas.message import MessageCreate
from app.utils.websocket_manager import manager


class MessageService_:

    def send_message(self, db: Session, sender_id: int, data: MessageCreate):
        # Validate receiver exists
        receiver = db.query(User).filter(User.id == data.receiver_id).first()
        if not receiver:
            raise HTTPException(status_code=404, detail="Recipient not found")

        if data.receiver_id == sender_id:
            raise HTTPException(status_code=400, detail="Cannot message yourself")

        # If booking_id provided, verify sender is actually part of that booking
        if data.booking_id:
            booking = db.query(Booking).filter(Booking.id == data.booking_id).first()
            if not booking:
                raise HTTPException(status_code=404, detail="Booking not found")

            vendor = db.query(VendorProfile).filter(VendorProfile.user_id == sender_id).first()
            is_customer = booking.customer_id == sender_id
            is_vendor = vendor and booking.vendor_id == vendor.id

            if not is_customer and not is_vendor:
                raise HTTPException(status_code=403, detail="You are not part of this booking")

        message = Message(
            booking_id=data.booking_id,
            sender_id=sender_id,
            receiver_id=data.receiver_id,
            content=data.content
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        try:
            asyncio.create_task(manager.send_to_user(data.receiver_id, {
                "type": "chat_message",
                "data": {
                    "id": message.id,
                    "booking_id": message.booking_id,
                    "sender_id": message.sender_id,
                    "receiver_id": message.receiver_id,
                    "content": message.content,
                    "created_at": message.created_at.isoformat()
                }
            }))
        except Exception:
            pass

        return message


    def get_conversation_by_booking(self, db: Session, user_id: int, booking_id: int):
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        vendor = db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()
        is_customer = booking.customer_id == user_id
        is_vendor = vendor and booking.vendor_id == vendor.id

        if not is_customer and not is_vendor:
            raise HTTPException(status_code=403, detail="Access denied")

        messages = db.query(Message).filter(
            Message.booking_id == booking_id
        ).order_by(Message.created_at.asc()).all()

        db.query(Message).filter(
            Message.booking_id == booking_id,
            Message.receiver_id == user_id,
            Message.is_read == False
        ).update({"is_read": True})
        db.commit()

        return messages


    def get_conversation_direct(self, db: Session, user_id: int, other_user_id: int):
        """Get all messages between two users that are NOT tied to any booking."""
        other_user = db.query(User).filter(User.id == other_user_id).first()
        if not other_user:
            raise HTTPException(status_code=404, detail="User not found")

        messages = db.query(Message).filter(
            Message.booking_id.is_(None),
            or_(
                and_(Message.sender_id == user_id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == user_id)
            )
        ).order_by(Message.created_at.asc()).all()

        db.query(Message).filter(
            Message.booking_id.is_(None),
            Message.sender_id == other_user_id,
            Message.receiver_id == user_id,
            Message.is_read == False
        ).update({"is_read": True})
        db.commit()

        return messages


    def get_my_conversations(self, db: Session, user_id: int):
        vendor = db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()
        results = []
        seen_keys = set()

        # ── Booking-tied conversations ──
        booking_query = db.query(Booking).filter(
            or_(
                Booking.customer_id == user_id,
                Booking.vendor_id == (vendor.id if vendor else -1)
            )
        )

        for booking in booking_query.all():
            last_msg = db.query(Message).filter(
                Message.booking_id == booking.id
            ).order_by(Message.created_at.desc()).first()

            if not last_msg:
                continue

            unread = db.query(Message).filter(
                Message.booking_id == booking.id,
                Message.receiver_id == user_id,
                Message.is_read == False
            ).count()

            if booking.customer_id == user_id:
                other_vendor = db.query(VendorProfile).filter(VendorProfile.id == booking.vendor_id).first()
                other_name = other_vendor.business_name if other_vendor else "Vendor"
                other_id = other_vendor.user_id if other_vendor else None
            else:
                customer = db.query(User).filter(User.id == booking.customer_id).first()
                other_name = customer.name if customer else "Customer"
                other_id = customer.id if customer else None

            key = f"booking_{booking.id}"
            seen_keys.add(key)
            results.append({
                "conversation_key": key,
                "booking_id": booking.id,
                "booking_ref": booking.booking_ref,
                "other_user_id": other_id,
                "other_user_name": other_name,
                "last_message": last_msg.content,
                "last_message_at": last_msg.created_at,
                "unread_count": unread
            })

        # ── Direct (no booking) conversations ──
        direct_messages = db.query(Message).filter(
            Message.booking_id.is_(None),
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        ).order_by(Message.created_at.desc()).all()

        direct_partners = {}
        for msg in direct_messages:
            other_id = msg.receiver_id if msg.sender_id == user_id else msg.sender_id
            if other_id not in direct_partners:
                direct_partners[other_id] = msg

            for other_id, last_msg in direct_partners.items():
                other_user = db.query(User).filter(User.id == other_id).first()
                if not other_user:
                    continue

                other_vendor = db.query(VendorProfile).filter(VendorProfile.user_id == other_id).first()
                display_name = other_vendor.business_name if other_vendor else other_user.name

                unread = db.query(Message).filter(
                    Message.booking_id.is_(None),
                    Message.sender_id == other_id,
                    Message.receiver_id == user_id,
                    Message.is_read == False
                ).count()

                key = f"user_{other_id}"
                results.append({
                    "conversation_key": key,
                    "booking_id": None,
                    "booking_ref": None,
                    "other_user_id": other_id,
                    "other_user_name": display_name,
                    "last_message": last_msg.content,
                    "last_message_at": last_msg.created_at,
                    "unread_count": unread
                })

            results.sort(key=lambda x: x["last_message_at"], reverse=True)
        return results


message_service = MessageService_()