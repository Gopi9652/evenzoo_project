import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-approval-banner',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  templateUrl: './approval-banner.component.html',
  styleUrl: './approval-banner.component.scss'
})
export class ApprovalBannerComponent implements OnInit {
  isApproved: boolean | null = null;
  rejectionReason: string | null = null;
  loading = true;
  dismissed = false;

  constructor(private authService: AuthService) {}

  ngOnInit() {
    // Only vendors need this check
    if (this.authService.getRole() !== 'vendor') {
      this.loading = false;
      return;
    }

    this.authService.getVendorApprovalStatus().subscribe({
      next: (data) => {
        this.isApproved = data.is_approved;
        this.rejectionReason = data.rejection_reason;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  get shouldShow(): boolean {
    return !this.loading && this.isApproved === false && !this.dismissed;
  }

  dismiss() {
    this.dismissed = true;
  }
}