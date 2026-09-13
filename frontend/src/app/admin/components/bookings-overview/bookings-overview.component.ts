import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { FormsModule } from '@angular/forms';
import { AdminService } from '../../../core/services/admin.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { Router } from '@angular/router';
@Component({
  selector: 'app-bookings-overview',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatSelectModule, MatButtonModule,
    MatIconModule, MatProgressSpinnerModule, NavbarComponent
  ],
  templateUrl: './bookings-overview.component.html',
  styleUrl: './bookings-overview.component.scss'
})
export class BookingsOverviewComponent implements OnInit {
  bookings: any[] = [];
  loading = true;
  statusFilter = '';

  constructor(private adminService: AdminService,  private router: Router) {}

  ngOnInit() {
    this.loadBookings();
  }

  loadBookings() {
    this.loading = true;
    this.adminService.getAllBookings(this.statusFilter || undefined).subscribe({
      next: (data) => {
        this.bookings = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  onFilterChange() {
    this.loadBookings();
  }

  forceCancel(booking: any) {
    const reason = prompt('Reason for admin cancellation (dispute resolution):');
    if (!reason) return;

    this.adminService.forceCancelBooking(booking.id, reason).subscribe({
      next: () => this.loadBookings(),
      error: (err) => alert(err.error?.detail || 'Failed to cancel booking')
    });
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
  viewDetail(bookingId: number) {
    this.router.navigate(['/admin/bookings', bookingId]);
  }
}