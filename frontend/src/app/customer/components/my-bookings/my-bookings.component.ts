import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatTabsModule } from '@angular/material/tabs';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BookingService } from '../../../core/services/booking.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { Booking } from '../../../core/models/booking.model';

@Component({
  selector: 'app-my-bookings',
  standalone: true,
  imports: [
    CommonModule, MatTabsModule, MatIconModule,
    MatProgressSpinnerModule, NavbarComponent
  ],
  templateUrl: './my-bookings.component.html',
  styleUrl: './my-bookings.component.scss'
})
export class MyBookingsComponent implements OnInit {
  allBookings: Booking[] = [];
  loading = true;

  constructor(
    private bookingService: BookingService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadBookings();
  }

  loadBookings() {
    this.loading = true;
    this.bookingService.getMyBookings().subscribe({
      next: (data) => {
        this.allBookings = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load bookings', err);
        this.loading = false;
      }
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

  viewBooking(bookingId: number) {
    this.router.navigate(['/customer/booking', bookingId]);
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

  statusIcon(status: string): string {
    const icons: Record<string, string> = {
      pending: 'schedule',
      confirmed: 'check_circle',
      completed: 'task_alt',
      cancelled: 'cancel'
    };
    return icons[status] || 'info';
  }
}