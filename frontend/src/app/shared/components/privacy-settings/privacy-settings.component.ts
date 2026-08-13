import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { PrivacyService } from '../../../core/services/privacy.service';
import { AuthService } from '../../../core/services/auth.service';
import { NavbarComponent } from '../navbar/navbar.component';

@Component({
  selector: 'app-privacy-settings',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule, NavbarComponent],
  templateUrl: './privacy-settings.component.html',
  styleUrl: './privacy-settings.component.scss'
})
export class PrivacySettingsComponent implements OnInit {
  pendingRequests: any[] = [];
  loading = true;
  exporting = false;
  requestingDeletion = false;

  constructor(
    private privacyService: PrivacyService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadRequests();
  }

  loadRequests() {
    this.loading = true;
    this.privacyService.getMyDeletionRequests().subscribe({
      next: (data) => {
        this.pendingRequests = data.filter(r => r.status === 'pending');
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  exportData() {
    this.exporting = true;
    this.privacyService.exportMyData().subscribe({
      next: (data) => {
        this.exporting = false;
        this.downloadJson(data);
      },
      error: (err) => {
        this.exporting = false;
        alert(err.error?.detail || 'Failed to export data');
      }
    });
  }

  downloadJson(data: any) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `evenzoo-my-data-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
  }

  requestDeletion() {
    const confirmed = confirm(
      'Are you sure you want to request account deletion?\n\n' +
      'Your account will be immediately deactivated while an admin reviews your request. ' +
      'Once processed, your personal information (name, email, phone) will be permanently anonymized. ' +
      'This cannot be undone.'
    );

    if (!confirmed) return;

    const reason = prompt('Optional: tell us why you\'re leaving (helps us improve)') || undefined;

    this.requestingDeletion = true;
    this.privacyService.requestDeletion(reason).subscribe({
      next: () => {
        this.requestingDeletion = false;
        alert('Your deletion request has been submitted. Your account is now deactivated and will be permanently anonymized once reviewed. You will be logged out now.');
        this.authService.clearSession();
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.requestingDeletion = false;
        alert(err.error?.detail || 'Failed to submit deletion request');
      }
    });
  }

  cancelRequest(requestId: number) {
    if (!confirm('Cancel this deletion request and reactivate your account?')) return;

    this.privacyService.cancelDeletionRequest(requestId).subscribe({
      next: () => {
        alert('Deletion request cancelled. Your account is active again.');
        this.loadRequests();
      },
      error: (err) => alert(err.error?.detail || 'Failed to cancel request')
    });
  }
}