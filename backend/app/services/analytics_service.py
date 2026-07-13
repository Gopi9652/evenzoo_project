from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta

from app.models.booking import Booking
from app.models.review import Review
from app.models.payment import Payment
from app.models.vendor import VendorProfile


class AnalyticsService_:

    def get_vendor_analytics(self, db: Session, vendor_id: int):
        vendor = db.query(VendorProfile).filter(VendorProfile.id == vendor_id).first()

        # Bookings over last 6 months, grouped by month
        six_months_ago = datetime.utcnow() - timedelta(days=180)

        monthly_bookings = db.query(
            extract('month', Booking.created_at).label('month'),
            extract('year', Booking.created_at).label('year'),
            func.count(Booking.id).label('count')
        ).filter(
            Booking.vendor_id == vendor_id,
            Booking.created_at >= six_months_ago
        ).group_by('year', 'month').order_by('year', 'month').all()

        # Revenue over the same period (only captured payments)
        monthly_revenue = db.query(
            extract('month', Booking.created_at).label('month'),
            extract('year', Booking.created_at).label('year'),
            func.coalesce(func.sum(Booking.vendor_amount), 0).label('revenue')
        ).join(Payment, Payment.booking_id == Booking.id).filter(
            Booking.vendor_id == vendor_id,
            Payment.status == 'captured',
            Booking.created_at >= six_months_ago
        ).group_by('year', 'month').order_by('year', 'month').all()

        # Booking status breakdown
        status_breakdown = db.query(
            Booking.status,
            func.count(Booking.id)
        ).filter(Booking.vendor_id == vendor_id).group_by(Booking.status).all()

        # Rating distribution (1-5 stars)
        rating_distribution = db.query(
            func.round(Review.overall_rating).label('rating'),
            func.count(Review.id)
        ).filter(Review.vendor_id == vendor_id).group_by('rating').all()

        # Conversion metrics
        total_bookings = db.query(Booking).filter(Booking.vendor_id == vendor_id).count()
        completed = db.query(Booking).filter(
            Booking.vendor_id == vendor_id, Booking.status == 'completed'
        ).count()
        cancelled = db.query(Booking).filter(
            Booking.vendor_id == vendor_id, Booking.status == 'cancelled'
        ).count()

        completion_rate = round((completed / total_bookings * 100), 1) if total_bookings > 0 else 0
        cancellation_rate = round((cancelled / total_bookings * 100), 1) if total_bookings > 0 else 0

        total_earnings = db.query(
            func.coalesce(func.sum(Booking.vendor_amount), 0)
        ).join(Payment, Payment.booking_id == Booking.id).filter(
            Booking.vendor_id == vendor_id,
            Payment.status == 'captured'
        ).scalar()

        return {
            "vendor_id": vendor_id,
            "business_name": vendor.business_name,
            "total_bookings": total_bookings,
            "completion_rate": completion_rate,
            "cancellation_rate": cancellation_rate,
            "total_earnings": float(total_earnings or 0),
            "avg_rating": float(vendor.avg_rating or 0),
            "total_reviews": vendor.total_reviews,
            "monthly_bookings": [
                {"month": int(m.month), "year": int(m.year), "count": m.count}
                for m in monthly_bookings
            ],
            "monthly_revenue": [
                {"month": int(m.month), "year": int(m.year), "revenue": float(m.revenue)}
                for m in monthly_revenue
            ],
            "status_breakdown": {status: count for status, count in status_breakdown},
            "rating_distribution": {int(rating): count for rating, count in rating_distribution if rating}
        }


analytics_service = AnalyticsService_()