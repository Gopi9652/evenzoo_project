from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.quote import Quote
from app.models.vendor import VendorProfile, VendorCategory
from app.models.user import User
from app.models.event_post import EventPost
from app.schemas.quote import QuoteRequestCreate, QuoteOfferCreate
from app.services.notification_service import notification_service
from app.services.engagement_service import engagement_service
from app.models.event_post_item import EventPostItem
from datetime import datetime
from datetime import datetime, timedelta
class QuoteService_:

    def request_quote(self, db: Session, customer_id: int, data: QuoteRequestCreate):
        """Customer explicitly asks a vendor for a price — creates a pending quote row with no amount yet."""
        vendor = db.query(VendorProfile).filter(
            VendorProfile.id == data.vendor_id,
            VendorProfile.is_approved == True
        ).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")

        if data.event_post_id:
            post = db.query(EventPost).filter(EventPost.id == data.event_post_id).first()
            if not post:
                raise HTTPException(status_code=404, detail="Event post not found")
            if post.customer_id != customer_id:
                raise HTTPException(status_code=403, detail="This is not your event post")
            if not post.allow_messages:
                raise HTTPException(status_code=400, detail="This customer has turned off quote requests for this post")

        quote = Quote(
            event_post_id=data.event_post_id,
            vendor_id=data.vendor_id,
            customer_id=customer_id,
            category_id=data.category_id,
            quoted_amount=0,          # placeholder until vendor actually responds
            message=data.message,
            status="pending",
            requested_by="customer"
        )
        db.add(quote)
        db.commit()
        db.refresh(quote)

        customer = db.query(User).filter(User.id == customer_id).first()
        notification_service.create(
            db,
            user_id=vendor.user_id,
            title="New Quote Request",
            message=f"{customer.name if customer else 'A customer'} requested a quote from you.",
            type="quote",
            link="/vendor/quotes"
        )
        engagement_service.track(db, data.vendor_id, "enquiry", customer_id)

        return self._attach_names(db, quote)


    def respond_to_quote(self, db: Session, user_id: int, quote_id: int, data: QuoteOfferCreate):
        """Vendor fills in the actual price on a pending quote request."""
        vendor = db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()
        quote = db.query(Quote).filter(
            Quote.id == quote_id,
            Quote.vendor_id == vendor.id if vendor else -1
        ).first()

        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")

        quote.quoted_amount = data.quoted_amount
        quote.message = data.message or quote.message
        quote.status = "pending"   # still pending customer's decision, now with a real price attached
        quote.responded_at = datetime.utcnow()

        db.commit()
        db.refresh(quote)

        customer_notif_name = vendor.business_name if vendor else "A vendor"
        notification_service.create(
            db,
            user_id=quote.customer_id,
            title="You Received a Quote",
            message=f"{customer_notif_name} sent you a quote of ₹{data.quoted_amount}.",
            type="quote",
            link="/customer/quotes"
        )
        engagement_service.track(db, vendor.id, "quote_sent", quote.customer_id)
        return self._attach_names(db, quote)


    def update_quote_status(self, db: Session, user_id: int, quote_id: int, new_status: str):
        """Customer accepts/declines a quote, or either party withdraws it."""
        quote = db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")

        vendor = db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()
        is_customer = quote.customer_id == user_id
        is_vendor = vendor and quote.vendor_id == vendor.id

        if not is_customer and not is_vendor:
            raise HTTPException(status_code=403, detail="Not authorized")

        if new_status not in {"accepted", "declined", "withdrawn"}:
            raise HTTPException(status_code=400, detail="Invalid status")

        quote.status = new_status
        from datetime import datetime
        quote.responded_at = datetime.utcnow()
        db.commit()
        db.refresh(quote)

        # Notify the other party
        notify_user_id = quote.vendor_id if is_customer else quote.customer_id
        if is_customer:
            vendor_row = db.query(VendorProfile).filter(VendorProfile.id == quote.vendor_id).first()
            notify_user_id = vendor_row.user_id if vendor_row else None

        if notify_user_id:
            notification_service.create(
                db, user_id=notify_user_id,
                title=f"Quote {new_status.title()}",
                message=f"Your quote was {new_status}.",
                type="quote",
                link="/vendor/quotes" if is_customer else "/customer/quotes"
            )

        return self._attach_names(db, quote)


    def get_my_quotes_as_customer(self, db: Session, customer_id: int, category_id: int = None):
        query = db.query(Quote).filter(Quote.customer_id == customer_id)
        if category_id:
            query = query.filter(Quote.category_id == category_id)
        quotes = query.order_by(Quote.quoted_amount.asc()).all()   # best (cheapest) to worst by default
        return [self._attach_names(db, q) for q in quotes]

    def _attach_names(self, db: Session, quote: Quote):
        vendor = db.query(VendorProfile).filter(VendorProfile.id == quote.vendor_id).first()
        customer = db.query(User).filter(User.id == quote.customer_id).first()

        quote.vendor_business_name = vendor.business_name if vendor else None
        quote.vendor_avg_rating = vendor.avg_rating if vendor else None
        quote.vendor_slug = vendor.slug if vendor else None
        quote.customer_name = customer.name if customer else None

        if quote.category_id:
            category = db.query(VendorCategory).filter(VendorCategory.id == quote.category_id).first()
            quote.category_name = category.name if category else None
        else:
            quote.category_name = None

        return quote
    def offer_quote_direct(self, db: Session, user_id: int, event_post_id: int, category_id, quoted_amount, message: str = None):
        vendor = db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor profile not found")

        post = db.query(EventPost).filter(EventPost.id == event_post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Event post not found")
        # Validate the chosen category is actually one the customer asked for on this post
        valid_category_ids = {item.category_id for item in db.query(EventPostItem).filter(EventPostItem.event_post_id == post.id).all()}
        if post.category_id:
            valid_category_ids.add(post.category_id)

        if category_id and category_id not in valid_category_ids:
            raise HTTPException(status_code=400, detail="This category wasn't requested in that post")
        if post.response_deadline and post.response_deadline < datetime.utcnow():
            raise HTTPException(status_code=400, detail="This post's quote deadline has passed")

        # Prevent a vendor quoting the same category on the same post twice — they can only update via respond, not duplicate
        existing = db.query(Quote).filter(
            Quote.event_post_id == event_post_id,
            Quote.vendor_id == vendor.id,
            Quote.category_id == category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="You've already sent a quote for this category on this post")

        quote = Quote(
            event_post_id=event_post_id,
            vendor_id=vendor.id,
            customer_id=post.customer_id,
            category_id=category_id,
            quoted_amount=quoted_amount,
            message=message,
            status="pending",
            requested_by="vendor"
        )
        db.add(quote)
        db.commit()
        db.refresh(quote)

        category_name = ""
        if category_id:
            cat = db.query(VendorCategory).filter(VendorCategory.id == category_id).first()
            category_name = f" for {cat.name}" if cat else ""

        notification_service.create(
            db, user_id=post.customer_id,
            title="You Received a Quote",
            message=f"{vendor.business_name} sent a quote of ₹{quoted_amount}{category_name} for your post \"{post.title}\".",
            type="quote",
            link="/customer/quotes"
        )
        engagement_service.track(db, vendor.id, "quote_sent", quote.customer_id)
        return self._attach_names(db, quote)


    def offer_bundle_quote(self, db: Session, user_id: int, event_post_id: int, items: list, message: str = None):
        """
        Lets a vendor quote several (or all) of a post's requested categories
        in one action — e.g. a vendor who does both photography and videography
        can send both prices at once instead of two separate round trips.
        """
        vendor = db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor profile not found")

        post = db.query(EventPost).filter(EventPost.id == event_post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Event post not found")
        valid_category_ids = {item.category_id for item in db.query(EventPostItem).filter(EventPostItem.event_post_id == post.id).all()}
        if post.category_id:
            valid_category_ids.add(post.category_id)

        if not items:
            raise HTTPException(status_code=400, detail="Select at least one category to quote")
        if post.response_deadline and post.response_deadline < datetime.utcnow():
            raise HTTPException(status_code=400, detail="This post's quote deadline has passed")
        created_quotes = []
        for entry in items:
            if entry.category_id not in valid_category_ids:
                raise HTTPException(status_code=400, detail=f"Category {entry.category_id} wasn't requested in this post")

            existing = db.query(Quote).filter(
                Quote.event_post_id == event_post_id,
                Quote.vendor_id == vendor.id,
                Quote.category_id == entry.category_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"You've already quoted category {entry.category_id} on this post")

            quote = Quote(
                event_post_id=event_post_id,
                vendor_id=vendor.id,
                customer_id=post.customer_id,
                category_id=entry.category_id,
                quoted_amount=entry.quoted_amount,
                message=message,
                status="pending",
                requested_by="vendor"
            )
            db.add(quote)
            created_quotes.append(quote)

        db.commit()
        for q in created_quotes:
            db.refresh(q)

        category_names = []
        for q in created_quotes:
            cat = db.query(VendorCategory).filter(VendorCategory.id == q.category_id).first()
            if cat:
                category_names.append(cat.name)

        notification_service.create(
            db, user_id=post.customer_id,
            title="You Received Multiple Quotes",
            message=f"{vendor.business_name} sent quotes for {', '.join(category_names)} on your post \"{post.title}\".",
            type="quote",
            link=f"/customer/quotes?post_id={post.id}"
        )

        
        notification_service.create(
            db, user_id=post.customer_id,
            title="You Received Multiple Quotes",
            message=f"{vendor.business_name} sent quotes for {', '.join(category_names)} on your post \"{post.title}\".",
            type="quote",
            link=f"/customer/quotes?post_id={post.id}"
        )
        engagement_service.track(db, vendor.id, "quote_sent", quote.customer_id)
        return [self._attach_names(db, q) for q in created_quotes]
    

    def get_my_quotes_as_customer(
            self, db: Session, customer_id: int,
            category_id: int = None, event_post_id: int = None,
            days: int = 30, from_date: datetime = None, to_date: datetime = None
        ):
            query = db.query(Quote).filter(Quote.customer_id == customer_id)

            if from_date:
                query = query.filter(Quote.created_at >= from_date)
            elif days:
                query = query.filter(Quote.created_at >= datetime.utcnow() - timedelta(days=days))

            if to_date:
                query = query.filter(Quote.created_at <= to_date)

            if category_id:
                query = query.filter(Quote.category_id == category_id)
            if event_post_id:
                query = query.filter(Quote.event_post_id == event_post_id)

            quotes = query.order_by(Quote.created_at.desc()).all()
            return [self._attach_names(db, q) for q in quotes]


    def get_my_quotes_as_vendor(
            self, db: Session, user_id: int,
            category_id: int = None, days: int = 30,
            from_date: datetime = None, to_date: datetime = None
        ):
            vendor = db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()
            if not vendor:
                raise HTTPException(status_code=404, detail="Vendor profile not found")

            query = db.query(Quote).filter(Quote.vendor_id == vendor.id)

            if from_date:
                query = query.filter(Quote.created_at >= from_date)
            elif days:
                query = query.filter(Quote.created_at >= datetime.utcnow() - timedelta(days=days))

            if to_date:
                query = query.filter(Quote.created_at <= to_date)

            if category_id:
                query = query.filter(Quote.category_id == category_id)

            quotes = query.order_by(Quote.created_at.desc()).all()
            return [self._attach_names(db, q) for q in quotes]
    def get_quote_summary_by_post(self, db: Session, customer_id: int):
        """
        Groups the customer's quotes by the post they belong to (plus a
        separate bucket for quotes that came from a direct vendor-profile
        request with no post attached), so multiple posts never blur together.
        """
        posts = db.query(EventPost).filter(EventPost.customer_id == customer_id).order_by(EventPost.created_at.desc()).all()

        summary = []
        for post in posts:
            quotes = db.query(Quote).filter(Quote.event_post_id == post.id).all()
            if not quotes:
                continue

            amounts = [float(q.quoted_amount) for q in quotes if q.quoted_amount and q.quoted_amount > 0]
            is_expired = post.event_date and post.event_date < datetime.utcnow()

            summary.append({
                "event_post_id": post.id,
                "post_title": post.title,
                "event_date": post.event_date,
                "is_expired": bool(is_expired),
                "quote_count": len(quotes),
                "lowest_quote": min(amounts) if amounts else None,
                "highest_quote": max(amounts) if amounts else None,
            })

        # Direct quotes (no post attached)
        direct_quotes = db.query(Quote).filter(
            Quote.customer_id == customer_id,
            Quote.event_post_id.is_(None)
        ).all()
        if direct_quotes:
            amounts = [float(q.quoted_amount) for q in direct_quotes if q.quoted_amount and q.quoted_amount > 0]
            summary.append({
                "event_post_id": None,
                "post_title": "Direct Vendor Enquiries",
                "event_date": None,
                "is_expired": False,
                "quote_count": len(direct_quotes),
                "lowest_quote": min(amounts) if amounts else None,
                "highest_quote": max(amounts) if amounts else None,
            })

        return summary
quote_service = QuoteService_()