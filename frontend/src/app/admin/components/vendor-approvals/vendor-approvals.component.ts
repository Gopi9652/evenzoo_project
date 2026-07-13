import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AdminService } from '../../../core/services/admin.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';

@Component({
  selector: 'app-vendor-approvals',
  standalone: true,
  imports: [
    CommonModule, MatTabsModule, MatButtonModule,
    MatIconModule, MatProgressSpinnerModule, NavbarComponent
  ],
  templateUrl: './vendor-approvals.component.html',
  styleUrl: './vendor-approvals.component.scss'
})
export class VendorApprovalsComponent implements OnInit {
  pendingVendors: any[] = [];
  approvedVendors: any[] = [];
  duplicates: any[] = [];
  loading = true;
  processingId: number | null = null;

  constructor(private adminService: AdminService) {}

  ngOnInit() {
    this.loadVendors();
  }

  loadVendors() {
    this.loading = true;
    this.adminService.getPendingVendors().subscribe({
      next: (data) => this.pendingVendors = data
    });
    this.adminService.getAllVendors(true).subscribe({
      next: (data) => {
        this.approvedVendors = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
    this.adminService.getDuplicateVendors().subscribe({
      next: (data) => this.duplicates = data,
      error: () => this.duplicates = []
    });
  }

  approveVendor(vendor: any) {
    this.processingId = vendor.id;
    this.adminService.reviewVendor(vendor.id, true).subscribe({
      next: () => {
        this.processingId = null;
        this.loadVendors();
      },
      error: (err) => {
        this.processingId = null;
        alert(err.error?.detail || 'Failed to approve vendor');
      }
    });
  }

  rejectVendor(vendor: any) {
    const reason = prompt('Reason for rejecting this vendor:');
    if (!reason) return;

    this.processingId = vendor.id;
    this.adminService.reviewVendor(vendor.id, false, reason).subscribe({
      next: () => {
        this.processingId = null;
        this.loadVendors();
      },
      error: (err) => {
        this.processingId = null;
        alert(err.error?.detail || 'Failed to reject vendor');
      }
    });
  }

  vendorName(id: number): string {
    const all = [...this.pendingVendors, ...this.approvedVendors];
    const found = all.find(v => v.id === id);
    return found ? found.business_name : `Vendor #${id}`;
  }
}