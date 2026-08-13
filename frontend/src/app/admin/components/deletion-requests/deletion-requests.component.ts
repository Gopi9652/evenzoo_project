import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { PrivacyService } from '../../../core/services/privacy.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';

@Component({
  selector: 'app-deletion-requests',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatProgressSpinnerModule, NavbarComponent],
  templateUrl: './deletion-requests.component.html',
  styleUrl: './deletion-requests.component.scss'
})
export class DeletionRequestsComponent implements OnInit {
  requests: any[] = [];
  loading = true;
  processingId: number | null = null;

  constructor(private privacyService: PrivacyService) {}

  ngOnInit() {
    this.loadRequests();
  }

  loadRequests() {
    this.loading = true;
    this.privacyService.getPendingDeletionRequests().subscribe({
      next: (data) => {
        this.requests = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  approve(request: any) {
    if (!confirm(`Permanently anonymize the account for ${request.user_email}? This cannot be undone.`)) return;

    this.processingId = request.id;
    this.privacyService.processDeletionRequest(request.id).subscribe({
      next: () => {
        this.processingId = null;
        this.loadRequests();
      },
      error: (err) => {
        this.processingId = null;
        alert(err.error?.detail || 'Failed to process request');
      }
    });
  }

  reject(request: any) {
    const reason = prompt('Reason for rejecting this deletion request:');
    if (!reason) return;

    this.processingId = request.id;
    this.privacyService.rejectDeletionRequest(request.id, reason).subscribe({
      next: () => {
        this.processingId = null;
        this.loadRequests();
      },
      error: (err) => {
        this.processingId = null;
        alert(err.error?.detail || 'Failed to reject request');
      }
    });
  }
}