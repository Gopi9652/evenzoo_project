import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { LoginRequest, LoginResponse, RegisterRequest, User } from '../models/user.model';
import { WebsocketService } from './websocket.service';
@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = `${environment.apiUrl}/auth`;

  constructor(private http: HttpClient, private ws: WebsocketService) {}

  register(data: RegisterRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, data);
  }



  logout(): Observable<any> {
    const refreshToken = localStorage.getItem('refresh_token');
    return this.http.post(`${this.apiUrl}/logout`, {
      refresh_token: refreshToken
    }).pipe(
      tap(() => this.clearSession())
    );
  }
  getMe(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/me`);
  }

  sendOtp(phone: string, purpose: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/send-otp`, { phone, purpose });
  }

  verifyOtp(phone: string, otp_code: string, purpose: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/verify-otp`, { phone, otp_code, purpose });
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRole(): string | null {
    return localStorage.getItem('role');
  }

  getUserId(): number | null {
    const id = localStorage.getItem('user_id');
    return id ? parseInt(id) : null;
  }
  forgotPassword(email: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/forgot-password`, { email });
  }

  resetPassword(token: string, new_password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/reset-password`, { token, new_password });
  }
  getVendorApprovalStatus(): Observable<{ is_approved: boolean; rejection_reason: string | null }> {
    return this.http.get<{ is_approved: boolean; rejection_reason: string | null }>(
      `${environment.apiUrl}/vendors/me/approval-status`
    );
  }

  changePassword(current_password: string, new_password: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/change-password`, { current_password, new_password });
  }
  uploadAvatar(file: File): Observable<{ profile_photo: string }> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{ profile_photo: string }>(`${this.apiUrl}/me/avatar`, formData);
  }
  getSessions(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/sessions`);
  }

  revokeSession(sessionId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/sessions/${sessionId}`);
  }

  revokeAllSessions(): Observable<any> {
    return this.http.delete(`${this.apiUrl}/sessions`);
  }


// In the constructor:


// Update login():
login(data: LoginRequest): Observable<LoginResponse> {
  return this.http.post<LoginResponse>(`${this.apiUrl}/login`, data).pipe(
    tap(response => {
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      localStorage.setItem('role', response.role);
      localStorage.setItem('user_id', response.user_id.toString());
      localStorage.setItem('name', response.name);
      this.ws.connect();
    })
  );
}

// Update clearSession():
clearSession(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('role');
  localStorage.removeItem('user_id');
  localStorage.removeItem('name');
  this.ws.disconnect();
}

}