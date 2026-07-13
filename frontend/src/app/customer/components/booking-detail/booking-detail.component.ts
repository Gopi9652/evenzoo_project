import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BookingService } from '../../../core/services/booking.service';
import { PaymentService } from '../../../core/services/payment.service';
import { AuthService } from '../../../core/services/auth.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { Booking } from '../../../core/models/booking.model';
import { RazorpayOptions, RazorpayResponse } from '../../../core/models/razorpay.model';
import { ReviewService } from '../../../core/services/review.service';
import { VendorService } from '../../../core/services/vendor.service';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-booking-detail',
  standalone: true,
  imports: [
    CommonModule, MatIconModule, MatButtonModule,
    MatProgressSpinnerModule, NavbarComponent, FormsModule
  ],
  templateUrl: './booking-detail.component.html',
  styleUrl: './booking-detail.component.scss'
})
export class BookingDetailComponent implements OnInit {
  booking: Booking | null = null;
  history: any[] = [];
  paymentStatus: string | null = null;
  loading = true;
  cancelling = false;
  payingNow = false;
  existingReview: any = null;
  editingReview = false;
  reviewForm = {
    quality_rating: 5,
    price_rating: 5,
    service_rating: 5,
    title: '',
    body: ''
  };
  vendorUserId: number | null = null;
  vendorName = '';

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private bookingService: BookingService,
    private paymentService: PaymentService,
    private authService: AuthService,
    private reviewService: ReviewService,
    private vendorService: VendorService,
  ) {}

  ngOnInit() {
    const bookingId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadBooking(bookingId);
  }



// Inside loadBooking(), after getting the booking, fetch vendor info:
loadBooking(bookingId: number) {
  this.loading = true;
  this.bookingService.getBooking(bookingId).subscribe({
    next: (data) => {
      this.booking = data;
      this.loading = false;
      this.checkPaymentStatus(bookingId);
      this.loadVendorInfo(data.vendor_id);
    },
    error: (err) => {
      console.error('Failed to load booking', err);
      this.loading = false;
    }
  });

  this.bookingService.getBookingHistory(bookingId).subscribe({
    next: (data) => this.history = data
  });
}

loadVendorInfo(vendorId: number) {
  this.vendorService.getVendorDetail(vendorId).subscribe({
    next: (v: any) => {
      this.vendorUserId = v.user_id;
      this.vendorName = v.business_name;
    }
  });
}


  checkPaymentStatus(bookingId: number) {
    this.paymentService.getPaymentStatus(bookingId).subscribe({
      next: (data) => this.paymentStatus = data.status,
      error: () => this.paymentStatus = null // no payment created yet, that's fine
    });
  }

  cancelBooking() {
    if (!this.booking) return;

    const reason = prompt('Please tell us why you are cancelling:');
    if (!reason) return;

    this.cancelling = true;
    this.bookingService.updateStatus(this.booking.id, 'cancelled', reason).subscribe({
      next: () => {
        this.cancelling = false;
        this.loadBooking(this.booking!.id);
      },
      error: (err) => {
        this.cancelling = false;
        alert(err.error?.detail || 'Failed to cancel booking');
      }
    });
  }

  payNow() {
    if (!this.booking) return;

    this.payingNow = true;

    this.paymentService.createOrder(this.booking.id).subscribe({
      next: (orderData) => {
        this.openRazorpayCheckout(orderData);
      },
      error: (err) => {
        this.payingNow = false;
        alert(err.error?.detail || 'Failed to initiate payment');
      }
    });
  }

  openRazorpayCheckout(orderData: any) {
    const userName = localStorage.getItem('name') || '';

    const options: RazorpayOptions = {
      key: orderData.key_id,
      amount: orderData.amount,
      currency: orderData.currency,
      name: 'Evenzoo',
      description: `Booking ${orderData.booking_ref}`,
      order_id: orderData.order_id,
      handler: (response: RazorpayResponse) => {
        this.verifyPayment(response);
      },
      prefill: {
        name: userName
      },
      theme: {
        color: '#e8650a'
      },
      modal: {
        ondismiss: () => {
          this.payingNow = false;
        }
      }
    };

    const razorpayInstance = new window.Razorpay(options);
    razorpayInstance.open();
  }

  verifyPayment(response: RazorpayResponse) {
    if (!this.booking) return;

    this.paymentService.verifyPayment({
      booking_id: this.booking.id,
      razorpay_order_id: response.razorpay_order_id,
      razorpay_payment_id: response.razorpay_payment_id,
      razorpay_signature: response.razorpay_signature
    }).subscribe({
      next: () => {
        this.payingNow = false;
        alert('Payment successful! 🎉');
        this.loadBooking(this.booking!.id);
      },
      error: (err) => {
        this.payingNow = false;
        alert(err.error?.detail || 'Payment verification failed. Please contact support.');
      }
    });
  }

  get canCancel(): boolean {
    return this.booking?.status === 'pending' || this.booking?.status === 'confirmed';
  }

  get needsPayment(): boolean {
    return this.booking?.status === 'confirmed' && this.paymentStatus !== 'captured';
  }

  get isPaid(): boolean {
    return this.paymentStatus === 'captured';
  }

  statusColor(status: string): string {
    const colors: Record<string, string> = {
      pending: '#f5a623',
      confirmed: '#e8650a',
      completed: '#16a34a',
      cancelled: '#dc2626'
    };
    return colors[status] || '#64748b';
  }

// Add these methods inside the class
loadMyReview() {
  if (!this.booking) return;
  this.reviewService.getVendorReviews(this.booking.vendor_id).subscribe({
    next: (reviews) => {
      this.existingReview = reviews.find((r: any) => r.booking_id === this.booking!.id) || null;
      if (this.existingReview) {
        this.reviewForm = {
          quality_rating: this.existingReview.quality_rating,
          price_rating: this.existingReview.price_rating,
          service_rating: this.existingReview.service_rating,
          title: this.existingReview.title || '',
          body: this.existingReview.body || ''
        };
      }
    }
  });
}

submitReview() {
  if (!this.booking) return;

  if (this.existingReview) {
    this.reviewService.updateReview(this.existingReview.id, this.reviewForm).subscribe({
      next: () => {
        alert('Review updated!');
        this.editingReview = false;
        this.loadMyReview();
      },
      error: (err) => alert(err.error?.detail || 'Failed to update review')
    });
  } else {
    this.reviewService.createReview({
      booking_id: this.booking.id,
      ...this.reviewForm
    }).subscribe({
      next: () => {
        alert('Review submitted!');
        this.editingReview = false;
        this.loadMyReview();
      },
      error: (err) => alert(err.error?.detail || 'Failed to submit review')
    });
  }
}

deleteMyReview() {
  if (!this.existingReview) return;
  if (!confirm('Delete your review? This cannot be undone.')) return;

  this.reviewService.deleteReview(this.existingReview.id).subscribe({
    next: () => {
      alert('Review deleted');
      this.existingReview = null;
      this.reviewForm = { quality_rating: 5, price_rating: 5, service_rating: 5, title: '', body: '' };
    },
    error: (err) => alert(err.error?.detail || 'Failed to delete review')
  });
}
}