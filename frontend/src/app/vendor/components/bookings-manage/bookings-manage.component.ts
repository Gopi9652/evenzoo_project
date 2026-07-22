import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BookingService } from '../../../core/services/booking.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { Booking } from '../../../core/models/booking.model';
import { ApprovalBannerComponent } from '../../../shared/components/approval-banner/approval-banner.component';
import { AuthService } from '../../../core/services/auth.service';
import { environment } from '../../../../environments/environment';
@Component({
  selector: 'app-bookings-manage',
  standalone: true,
  imports: [
    CommonModule, MatTabsModule, MatButtonModule,
    MatIconModule, MatProgressSpinnerModule, NavbarComponent, ApprovalBannerComponent,
  ],
  templateUrl: './bookings-manage.component.html',
  styleUrl: './bookings-manage.component.scss'
})
export class BookingsManageComponent implements OnInit {
  allBookings: Booking[] = [];
  loading = true;
  processingId: number | null = null;
  isApproved: boolean | null = null;
  paymentsEnabled = environment.paymentsEnabled;

  constructor(private bookingService: BookingService,  private authService: AuthService) {}

  ngOnInit() {
    this.loadBookings();
    this.authService.getVendorApprovalStatus().subscribe({
      next: (data) => this.isApproved = data.is_approved
    });
  }

  loadBookings() {
    this.loading = true;
    this.bookingService.getVendorBookings().subscribe({
      next: (data) => {
        this.allBookings = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  get pendingBookings(): Booking[] {
    return this.allBookings.filter(b => b.status === 'pending');
  }

  get confirmedBookings(): Booking[] {
    return this.allBookings.filter(b => b.status === 'confirmed');
  }

  get completedBookings(): Booking[] {
    return this.allBookings.filter(b => b.status === 'completed');
  }

  get cancelledBookings(): Booking[] {
    return this.allBookings.filter(b => b.status === 'cancelled');
  }

  acceptBooking(booking: Booking) {
    this.processingId = booking.id;
    this.bookingService.updateStatus(booking.id, 'confirmed').subscribe({
      next: () => {
        this.processingId = null;
        this.loadBookings();
      },
      error: (err) => {
        this.processingId = null;
        alert(err.error?.detail || 'Failed to confirm booking');
      }
    });
  }

  rejectBooking(booking: Booking) {
    const reason = prompt('Reason for declining this booking:');
    if (!reason) return;

    this.processingId = booking.id;
    this.bookingService.updateStatus(booking.id, 'cancelled', reason).subscribe({
      next: () => {
        this.processingId = null;
        this.loadBookings();
      },
      error: (err) => {
        this.processingId = null;
        alert(err.error?.detail || 'Failed to decline booking');
      }
    });
  }

  markCompleted(booking: Booking) {
    if (!confirm('Mark this booking as completed? This cannot be undone.')) return;

    this.processingId = booking.id;
    this.bookingService.updateStatus(booking.id, 'completed').subscribe({
      next: () => {
        this.processingId = null;
        this.loadBookings();
      },
      error: (err) => {
        this.processingId = null;
        alert(err.error?.detail || 'Failed to mark as completed');
      }
    });
  }
}