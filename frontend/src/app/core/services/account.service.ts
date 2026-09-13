import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AccountService {
  private apiUrl = `${environment.apiUrl}/account`;

  constructor(private http: HttpClient) {}

  requestEmailChange(newEmail: string, currentPassword: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/change-email`, {
      new_email: newEmail,
      current_password: currentPassword
    });
  }

  confirmEmailChange(token: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/confirm-email-change`, { token });
  }

  cancelEmailChange(): Observable<any> {
    return this.http.delete(`${this.apiUrl}/change-email`);
  }

  requestPhoneChange(newPhone: string, currentPassword: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/change-phone`, {
      new_phone: newPhone,
      current_password: currentPassword
    });
  }

  verifyPhoneChange(otpCode: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/verify-phone-change`, { otp_code: otpCode });
  }

  resendPhoneChangeOtp(): Observable<any> {
    return this.http.post(`${this.apiUrl}/resend-phone-change-otp`, {});
  }

  cancelPhoneChange(): Observable<any> {
    return this.http.delete(`${this.apiUrl}/change-phone`);
  }

  getPendingChanges(): Observable<{ pending_email: string | null; pending_phone: string | null }> {
    return this.http.get<any>(`${this.apiUrl}/pending-changes`);
  }
}