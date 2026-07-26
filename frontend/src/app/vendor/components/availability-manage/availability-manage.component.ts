import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { VendorService } from '../../../core/services/vendor.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { MatFormFieldModule } from '@angular/material/form-field';
@Component({
  selector: 'app-availability-manage',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatDatepickerModule, MatNativeDateModule,
    MatButtonModule, MatIconModule, MatProgressSpinnerModule, NavbarComponent, MatFormFieldModule
  ],
  templateUrl: './availability-manage.component.html',
  styleUrl: './availability-manage.component.scss'
})
export class AvailabilityManageComponent implements OnInit {
  vendorId!: number;
  blockedDates: any[] = [];
  selectedDate: Date | null = null;
  reason = '';
  loading = true;
  saving = false;
  minDate = new Date();

  constructor(private vendorService: VendorService) {}

  ngOnInit() {
    this.vendorService.getMyProfile().subscribe({
      next: (profile) => {
        this.vendorId = profile.id;
        this.loadAvailability();
      },
      error: () => this.loading = false
    });
  }

  loadAvailability() {
    this.loading = true;
    this.vendorService.getMyAvailability(this.vendorId).subscribe({
      next: (data) => {
        // Only show dates explicitly marked unavailable — that's what matters to a vendor managing their calendar
        this.blockedDates = data.filter(d => !d.is_available);
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  blockDate() {
    if (!this.selectedDate) return;

    this.saving = true;
    const dateStr = this.selectedDate.toISOString().split('T')[0];

    this.vendorService.setAvailability({
      date: dateStr,
      is_available: false,
      reason: this.reason || 'Not available'
    }).subscribe({
      next: () => {
        this.saving = false;
        this.selectedDate = null;
        this.reason = '';
        this.loadAvailability();
      },
      error: (err) => {
        this.saving = false;
        alert(err.error?.detail || 'Failed to block date');
      }
    });
  }

  unblockDate(dateStr: string) {
    if (!confirm('Make this date available again?')) return;

    this.vendorService.setAvailability({
      date: dateStr,
      is_available: true
    }).subscribe({
      next: () => this.loadAvailability(),
      error: (err) => alert(err.error?.detail || 'Failed to unblock date')
    });
  }
}