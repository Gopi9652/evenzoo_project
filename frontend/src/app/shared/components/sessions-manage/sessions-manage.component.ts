import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../../../core/services/auth.service';
import { NavbarComponent } from '../navbar/navbar.component';

@Component({
  selector: 'app-sessions-manage',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule, NavbarComponent],
  templateUrl: './sessions-manage.component.html',
  styleUrl: './sessions-manage.component.scss'
})
export class SessionsManageComponent implements OnInit {
  sessions: any[] = [];
  loading = true;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadSessions();
  }

  loadSessions() {
    this.loading = true;
    this.authService.getSessions().subscribe({
      next: (data) => {
        this.sessions = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  revoke(sessionId: number) {
    if (!confirm('Log out this device?')) return;
    this.authService.revokeSession(sessionId).subscribe({
      next: () => this.loadSessions(),
      error: (err) => alert(err.error?.detail || 'Failed to revoke session')
    });
  }

  revokeAll() {
    if (!confirm('Log out of ALL other devices? You will stay logged in here.')) return;
    this.authService.revokeAllSessions().subscribe({
      next: () => this.loadSessions(),
      error: (err) => alert(err.error?.detail || 'Failed to revoke sessions')
    });
  }

  deviceIcon(deviceInfo: string): string {
    if (!deviceInfo) return 'devices_other';
    if (deviceInfo.includes('Android') || deviceInfo.includes('iOS')) return 'smartphone';
    if (deviceInfo.includes('Mac') || deviceInfo.includes('Windows')) return 'computer';
    return 'devices_other';
  }
}