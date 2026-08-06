import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatBadgeModule } from '@angular/material/badge';
import { Subscription } from 'rxjs';
import { AuthService } from '../../../core/services/auth.service';
import { WebsocketService } from '../../../core/services/websocket.service';
import { NotificationService } from '../../../core/services/notification.service';
@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, MatIconModule, MatButtonModule, MatMenuModule, MatBadgeModule],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss'
})
export class NavbarComponent implements OnInit, OnDestroy {
  notifications: any[] = [];
  unreadCount = 0;
  menuOpen = false;
  private wsSubscription?: Subscription;

  constructor(
    public authService: AuthService,
    private router: Router,
    private ws: WebsocketService,
    private notificationService: NotificationService
  ) {}

  ngOnInit() {
    this.loadNotifications();

    this.wsSubscription = this.ws.onMessage().subscribe((msg) => {
      if (msg.type === 'notification') {
        this.notifications = [msg.data, ...this.notifications].slice(0, 10);  // new array
        this.unreadCount++;
      }
    });
  }

  ngOnDestroy() {
    this.wsSubscription?.unsubscribe();
  }

  loadNotifications() {
    this.notificationService.getMyNotifications(false).subscribe({
      next: (data) => this.notifications = data.slice(0, 10)
    });
    this.notificationService.getUnreadCount().subscribe({
      next: (data) => this.unreadCount = data.unread_count
    });
  }

  markAllRead() {
    this.notificationService.markAllRead().subscribe({
      next: () => {
        this.unreadCount = 0;
      }
    });
  }

  get userName(): string {
    return localStorage.getItem('name') || 'User';
  }

  get userInitial(): string {
    return this.userName.charAt(0).toUpperCase();
  }

  logout() {
    this.authService.logout().subscribe({
      next: () => this.router.navigate(['/login']),
      error: () => {
        this.authService.clearSession();
        this.router.navigate(['/login']);
      }
    });
  }
  handleNotificationClick(notif: any) {
    if (notif.link) {
      this.router.navigateByUrl(notif.link);
    }
    if (!notif.is_read) {
      this.notificationService.markRead(notif.id).subscribe({
        next: () => {
          notif.is_read = true;
          this.unreadCount = Math.max(0, this.unreadCount - 1);
        }
      });
    }
  }
}