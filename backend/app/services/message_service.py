from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException
import logging

from app.models.message import Message
from app.models.booking import Booking
from app.models.user import User
from app.models.vendor import VendorProfile
from app.schemas.message import MessageCreate
from app.utils.websocket_manager import manager
from app.utils.encryption import encrypt_message, decrypt_message


logger = logging.getLogger(__name__)


class MessageService_:

    # ============================================================
    # Helper: Convert database Message -> API response
    # ============================================================
    def _message_response(self, message: Message):
        """
        Database stores encrypted content.
        API always returns decrypted content.
        """

        return {
            "id": message.id,
            "booking_id": message.booking_id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": decrypt_message(message.content),
            "is_read": message.is_read,
            "created_at": message.created_at.isoformat()
                if message.created_at else None,
        }


    # ============================================================
    # SEND MESSAGE
    # ============================================================
    async def send_message(
        self,
        db: Session,
        sender_id: int,
        data: MessageCreate
    ):

        # --------------------------------------------------------
        # 1. Check receiver
        # --------------------------------------------------------
        receiver = (
            db.query(User)
            .filter(User.id == data.receiver_id)
            .first()
        )

        if not receiver:
            raise HTTPException(
                status_code=404,
                detail="Recipient not found"
            )

        # --------------------------------------------------------
        # 2. Prevent messaging yourself
        # --------------------------------------------------------
        if data.receiver_id == sender_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot message yourself"
            )

        # --------------------------------------------------------
        # 3. Validate booking if supplied
        # --------------------------------------------------------
        if data.booking_id:

            booking = (
                db.query(Booking)
                .filter(Booking.id == data.booking_id)
                .first()
            )

            if not booking:
                raise HTTPException(
                    status_code=404,
                    detail="Booking not found"
                )

            vendor = (
                db.query(VendorProfile)
                .filter(VendorProfile.user_id == sender_id)
                .first()
            )

            is_customer = (
                booking.customer_id == sender_id
            )

            is_vendor = (
                vendor is not None
                and booking.vendor_id == vendor.id
            )

            if not is_customer and not is_vendor:
                raise HTTPException(
                    status_code=403,
                    detail="You are not part of this booking"
                )

        # --------------------------------------------------------
        # 4. Encrypt BEFORE storing
        # --------------------------------------------------------
        encrypted_content = encrypt_message(data.content)

        message = Message(
            booking_id=data.booking_id,
            sender_id=sender_id,
            receiver_id=data.receiver_id,
            content=encrypted_content
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        # --------------------------------------------------------
        # 5. Decrypted response for frontend
        # --------------------------------------------------------
        response_data = self._message_response(message)

        # --------------------------------------------------------
        # 6. Send realtime WebSocket notification
        # --------------------------------------------------------
        try:

            await manager.send_to_user(
                data.receiver_id,
                {
                    "type": "chat_message",
                    "data": response_data
                }
            )

        except Exception as e:

            logger.error(
                f"WebSocket notification failed: {e}"
            )

        # --------------------------------------------------------
        # 7. NEVER return SQLAlchemy object directly
        # --------------------------------------------------------
        return response_data


    # ============================================================
    # GET BOOKING CONVERSATION
    # ============================================================
    def get_conversation_by_booking(
        self,
        db: Session,
        user_id: int,
        booking_id: int
    ):

        # --------------------------------------------------------
        # 1. Find booking
        # --------------------------------------------------------
        booking = (
            db.query(Booking)
            .filter(Booking.id == booking_id)
            .first()
        )

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        # --------------------------------------------------------
        # 2. Check access
        # --------------------------------------------------------
        vendor = (
            db.query(VendorProfile)
            .filter(VendorProfile.user_id == user_id)
            .first()
        )

        is_customer = (
            booking.customer_id == user_id
        )

        is_vendor = (
            vendor is not None
            and booking.vendor_id == vendor.id
        )

        if not is_customer and not is_vendor:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        # --------------------------------------------------------
        # 3. Get messages
        # --------------------------------------------------------
        messages = (
            db.query(Message)
            .filter(Message.booking_id == booking_id)
            .order_by(Message.created_at.asc())
            .all()
        )

        # --------------------------------------------------------
        # 4. Mark unread messages as read
        # --------------------------------------------------------
        (
            db.query(Message)
            .filter(
                Message.booking_id == booking_id,
                Message.receiver_id == user_id,
                Message.is_read == False
            )
            .update(
                {"is_read": True},
                synchronize_session=False
            )
        )

        db.commit()

        # --------------------------------------------------------
        # 5. Return decrypted messages
        # --------------------------------------------------------
        return [
            self._message_response(message)
            for message in messages
        ]


    # ============================================================
    # GET DIRECT CONVERSATION
    # ============================================================
    def get_conversation_direct(
        self,
        db: Session,
        user_id: int,
        other_user_id: int
    ):

        # --------------------------------------------------------
        # 1. Check other user
        # --------------------------------------------------------
        other_user = (
            db.query(User)
            .filter(User.id == other_user_id)
            .first()
        )

        if not other_user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # --------------------------------------------------------
        # 2. Get direct messages
        # --------------------------------------------------------
        messages = (
            db.query(Message)
            .filter(
                Message.booking_id.is_(None),
                or_(
                    and_(
                        Message.sender_id == user_id,
                        Message.receiver_id == other_user_id
                    ),
                    and_(
                        Message.sender_id == other_user_id,
                        Message.receiver_id == user_id
                    )
                )
            )
            .order_by(Message.created_at.asc())
            .all()
        )

        # --------------------------------------------------------
        # 3. Mark messages as read
        # --------------------------------------------------------
        (
            db.query(Message)
            .filter(
                Message.booking_id.is_(None),
                Message.sender_id == other_user_id,
                Message.receiver_id == user_id,
                Message.is_read == False
            )
            .update(
                {"is_read": True},
                synchronize_session=False
            )
        )

        db.commit()

        # --------------------------------------------------------
        # 4. Return decrypted messages
        # --------------------------------------------------------
        return [
            self._message_response(message)
            for message in messages
        ]


    # ============================================================
    # GET MY CONVERSATIONS
    # ============================================================
    def get_my_conversations(
        self,
        db: Session,
        user_id: int
    ):

        vendor = (
            db.query(VendorProfile)
            .filter(VendorProfile.user_id == user_id)
            .first()
        )

        results = []

        # ========================================================
        # BOOKING CONVERSATIONS
        # ========================================================

        booking_query = (
            db.query(Booking)
            .filter(
                or_(
                    Booking.customer_id == user_id,
                    Booking.vendor_id == (
                        vendor.id if vendor else -1
                    )
                )
            )
        )

        bookings = booking_query.all()

        for booking in bookings:

            # ----------------------------------------------------
            # Latest message
            # ----------------------------------------------------
            last_msg = (
                db.query(Message)
                .filter(
                    Message.booking_id == booking.id
                )
                .order_by(
                    Message.created_at.desc()
                )
                .first()
            )

            if not last_msg:
                continue

            # ----------------------------------------------------
            # Unread count
            # ----------------------------------------------------
            unread = (
                db.query(Message)
                .filter(
                    Message.booking_id == booking.id,
                    Message.receiver_id == user_id,
                    Message.is_read == False
                )
                .count()
            )

            # ----------------------------------------------------
            # Find other user
            # ----------------------------------------------------
            if booking.customer_id == user_id:

                other_vendor = (
                    db.query(VendorProfile)
                    .filter(
                        VendorProfile.id == booking.vendor_id
                    )
                    .first()
                )

                other_name = (
                    other_vendor.business_name
                    if other_vendor
                    else "Vendor"
                )

                other_id = (
                    other_vendor.user_id
                    if other_vendor
                    else None
                )

            else:

                customer = (
                    db.query(User)
                    .filter(
                        User.id == booking.customer_id
                    )
                    .first()
                )

                other_name = (
                    customer.name
                    if customer
                    else "Customer"
                )

                other_id = (
                    customer.id
                    if customer
                    else None
                )

            # ----------------------------------------------------
            # Decrypt latest message
            # ----------------------------------------------------
            decrypted_last_message = decrypt_message(
                last_msg.content
            )

            # ----------------------------------------------------
            # Add result
            # ----------------------------------------------------
            results.append({
                "conversation_key": f"booking_{booking.id}",
                "booking_id": booking.id,
                "booking_ref": booking.booking_ref,
                "other_user_id": other_id,
                "other_user_name": other_name,
                "last_message": decrypted_last_message,
                "last_message_at": last_msg.created_at,
                "unread_count": unread
            })


        # ========================================================
        # DIRECT CONVERSATIONS
        # ========================================================

        direct_messages = (
            db.query(Message)
            .filter(
                Message.booking_id.is_(None),
                or_(
                    Message.sender_id == user_id,
                    Message.receiver_id == user_id
                )
            )
            .order_by(
                Message.created_at.desc()
            )
            .all()
        )

        # --------------------------------------------------------
        # Keep latest message for each user
        # --------------------------------------------------------
        direct_partners = {}

        for msg in direct_messages:

            other_id = (
                msg.receiver_id
                if msg.sender_id == user_id
                else msg.sender_id
            )

            if other_id not in direct_partners:
                direct_partners[other_id] = msg


        # --------------------------------------------------------
        # Build direct conversations
        # --------------------------------------------------------
        for other_id, last_msg in direct_partners.items():

            other_user = (
                db.query(User)
                .filter(User.id == other_id)
                .first()
            )

            if not other_user:
                continue

            other_vendor = (
                db.query(VendorProfile)
                .filter(
                    VendorProfile.user_id == other_id
                )
                .first()
            )

            display_name = (
                other_vendor.business_name
                if other_vendor
                else other_user.name
            )

            # ----------------------------------------------------
            # Unread count
            # ----------------------------------------------------
            unread = (
                db.query(Message)
                .filter(
                    Message.booking_id.is_(None),
                    Message.sender_id == other_id,
                    Message.receiver_id == user_id,
                    Message.is_read == False
                )
                .count()
            )

            # ----------------------------------------------------
            # Decrypt latest message
            # ----------------------------------------------------
            decrypted_last_message = decrypt_message(
                last_msg.content
            )

            # ----------------------------------------------------
            # Add result
            # ----------------------------------------------------
            results.append({
                "conversation_key": f"user_{other_id}",
                "booking_id": None,
                "booking_ref": None,
                "other_user_id": other_id,
                "other_user_name": display_name,
                "last_message": decrypted_last_message,
                "last_message_at": last_msg.created_at,
                "unread_count": unread
            })


        # ========================================================
        # SORT BY LATEST MESSAGE
        # ========================================================

        results.sort(
            key=lambda x: x["last_message_at"],
            reverse=True
        )

        return results


# ================================================================
# SERVICE INSTANCE
# ================================================================

message_service = MessageService_()