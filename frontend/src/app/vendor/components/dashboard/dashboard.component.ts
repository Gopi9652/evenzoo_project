import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { VendorService } from '../../../core/services/vendor.service';
import { BookingService } from '../../../core/services/booking.service';
import { AuthService } from '../../../core/services/auth.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { VendorProfile } from '../../../core/models/vendor.model';
import { Booking } from '../../../core/models/booking.model';
import { ApprovalBannerComponent } from '../../../shared/components/approval-banner/approval-banner.component';

@Component({
  selector: 'app-vendor-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, MatIconModule, MatProgressSpinnerModule, NavbarComponent, ApprovalBannerComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  profile: VendorProfile | null = null;
  recentBookings: Booking[] = [];
  loading = true;

  constructor(
    private vendorService: VendorService,
    private bookingService: BookingService,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.loadDashboardData();
  }

  loadDashboardData() {
    this.loading = true;

    // Get my profile via a direct API call since we need /me/profile
   // this.vendorService.listVendors().subscribe(); // no-op placeholder, real call below

    this.getMyProfile();
    this.getRecentBookings();
  }

  getMyProfile() {
    // We need a dedicated call — add to VendorService
    this.vendorService.getMyProfile().subscribe({
      next: (data) => {
        this.profile = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load profile', err);
        this.loading = false;
      }
    });
  }

  getRecentBookings() {
    this.bookingService.getVendorBookings().subscribe({
      next: (data) => this.recentBookings = data.slice(0, 5),
      error: (err) => console.error('Failed to load bookings', err)
    });
  }

  get pendingCount(): number {
    return this.recentBookings.filter(b => b.status === 'pending').length;
  }

  get isProfileIncomplete(): boolean {
    return !this.profile?.description || !this.profile?.address;
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
}