import { Injectable } from '@angular/core';

export type ConsentChoice = 'accepted' | 'essential_only';

@Injectable({ providedIn: 'root' })
export class ConsentService {
  private readonly CONSENT_KEY = 'cookie_consent';
  private readonly CONSENT_DATE_KEY = 'cookie_consent_date';

  getConsent(): ConsentChoice | null {
    return localStorage.getItem(this.CONSENT_KEY) as ConsentChoice | null;
  }

  hasConsented(): boolean {
    return this.getConsent() !== null;
  }

  setConsent(choice: ConsentChoice): void {
    localStorage.setItem(this.CONSENT_KEY, choice);
    localStorage.setItem(this.CONSENT_DATE_KEY, new Date().toISOString());
  }

  getConsentDate(): string | null {
    return localStorage.getItem(this.CONSENT_DATE_KEY);
  }

  /**
   * Evenzoo currently only uses strictly necessary storage (login session,
   * user preferences). There is no optional/marketing/analytics storage
   * to conditionally enable — so both consent choices result in identical
   * functional storage. This method exists so that if analytics or
   * marketing cookies are ever added in the future, this is the single
   * place to gate them behind actual "accepted" consent.
   */
  canUseNonEssentialStorage(): boolean {
    return this.getConsent() === 'accepted';
  }

  resetConsent(): void {
    localStorage.removeItem(this.CONSENT_KEY);
    localStorage.removeItem(this.CONSENT_DATE_KEY);
  }
}