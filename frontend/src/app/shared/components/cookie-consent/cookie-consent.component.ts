import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-cookie-consent',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './cookie-consent.component.html',
  styleUrl: './cookie-consent.component.scss'
})
export class CookieConsentComponent implements OnInit {
  showBanner = false;

  ngOnInit() {
    const consent = localStorage.getItem('cookie_consent');
    if (!consent) {
      this.showBanner = true;
    }
  }

  accept() {
    localStorage.setItem('cookie_consent', 'accepted');
    localStorage.setItem('cookie_consent_date', new Date().toISOString());
    this.showBanner = false;
  }

  decline() {
    // Since Evenzoo only uses essential cookies (login sessions), declining
    // still allows core functionality, but we record the preference.
    localStorage.setItem('cookie_consent', 'essential_only');
    localStorage.setItem('cookie_consent_date', new Date().toISOString());
    this.showBanner = false;
  }
}