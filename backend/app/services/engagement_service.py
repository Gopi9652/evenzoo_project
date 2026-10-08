from sqlalchemy.orm import Session
from app.models.vendor_event import VendorEngagementEvent


class EngagementService_:

    def track(self, db: Session, vendor_id: int, event_type: str, customer_id: int = None):
        event = VendorEngagementEvent(
            vendor_id=vendor_id,
            customer_id=customer_id,
            event_type=event_type
        )
        db.add(event)
        db.commit()


engagement_service = EngagementService_()