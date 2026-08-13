import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class PrivacyService {
  private apiUrl = `${environment.apiUrl}/privacy`;

  constructor(private http: HttpClient) {}

  requestDeletion(reason?: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/deletion-request`, { reason });
  }

  getMyDeletionRequests(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/deletion-request/my`);
  }

  cancelDeletionRequest(requestId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/deletion-request/${requestId}`);
  }

  exportMyData(): Observable<any> {
    return this.http.get(`${this.apiUrl}/export-my-data`);
  }

  // Admin
  getPendingDeletionRequests(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/admin/deletion-requests`);
  }

  processDeletionRequest(requestId: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/admin/deletion-requests/${requestId}/process`, {});
  }

  rejectDeletionRequest(requestId: number, reason: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/admin/deletion-requests/${requestId}/reject?reason=${encodeURIComponent(reason)}`, {});
  }
}