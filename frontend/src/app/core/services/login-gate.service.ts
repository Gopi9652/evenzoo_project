import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class LoginGateService {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  /**
   * Runs the action if logged in as a customer. Otherwise redirects
   * to login and remembers where to return afterwards.
   */
  requireCustomer(action: () => void, returnUrl?: string): void {
    if (!this.authService.isLoggedIn()) {
      this.redirectToLogin(returnUrl);
      return;
    }

    if (this.authService.getRole() !== 'customer') {
      alert('This action is only available to customer accounts.');
      return;
    }

    action();
  }

  requireLogin(action: () => void, returnUrl?: string): void {
    if (!this.authService.isLoggedIn()) {
      this.redirectToLogin(returnUrl);
      return;
    }
    action();
  }

  private redirectToLogin(returnUrl?: string) {
    const target = returnUrl || this.router.url;
    sessionStorage.setItem('post_login_redirect', target);
    this.router.navigate(['/login'], { queryParams: { reason: 'required' } });
  }
}