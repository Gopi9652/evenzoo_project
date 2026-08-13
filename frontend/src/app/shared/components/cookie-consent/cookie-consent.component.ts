import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ConsentService } from '../../../core/services/consent.service';

@Component({
  selector: 'app-cookie-consent',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './cookie-consent.component.html',
  styleUrl: './cookie-consent.component.scss'
})
export class CookieConsentComponent implements OnInit {
  showBanner = false;

  constructor(private consentService: ConsentService) {}

  ngOnInit() {
    this.showBanner = !this.consentService.hasConsented();
  }

  accept() {
    this.consentService.setConsent('accepted');
    this.showBanner = false;
  }

  decline() {
    this.consentService.setConsent('essential_only');
    this.showBanner = false;
  }
}