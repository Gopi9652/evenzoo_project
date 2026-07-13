import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface PlatformStats {
  total_users: number;
  total_customers: number;
  total_vendors: number;
  total_approved_vendors: number;
  pending_vendor_approvals: number;
  total_bookings: number;
  pending_bookings: number;
  confirmed_bookings: number;
  completed_bookings: number;
  cancelled_bookings: number;
  total_revenue: number;
  total_platform_commission: number;
  total_reviews: number;
  avg_platform_rating: number | null;
}

@Injectable({ providedIn: 'root' })
export class AdminService {
  private apiUrl = `${environment.apiUrl}/admin`;

  constructor(private http: HttpClient) {}

  getStats(): Observable<PlatformStats> {
    return this.http.get<PlatformStats>(`${this.apiUrl}/stats`);
  }

  getPendingVendors(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/vendors/pending`);
  }

  getAllVendors(approvedOnly?: boolean): Observable<any[]> {
    let url = `${this.apiUrl}/vendors`;
    if (approvedOnly !== undefined) url += `?approved_only=${approvedOnly}`;
    return this.http.get<any[]>(url);
  }

  reviewVendor(vendorId: number, isApproved: boolean, rejectionReason?: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/vendors/${vendorId}/review`, {
      is_approved: isApproved,
      rejection_reason: rejectionReason
    });
  }

  getAllBookings(status?: string): Observable<any[]> {
    let url = `${this.apiUrl}/bookings`;
    if (status) url += `?status=${status}`;
    return this.http.get<any[]>(url);
  }

  forceCancelBooking(bookingId: number, reason: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/bookings/${bookingId}/force-cancel?reason=${encodeURIComponent(reason)}`, {});
  }

  toggleUserStatus(userId: number, isActive: boolean): Observable<any> {
    return this.http.put(`${this.apiUrl}/users/${userId}/status?is_active=${isActive}`, {});
  }
  getDuplicateVendors(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/vendors/duplicates`);
  }
  getAllUsers(role?: string, activeOnly?: boolean): Observable<any[]> {
    let url = `${this.apiUrl}/users`;
    const params: string[] = [];
    if (role) params.push(`role=${role}`);
    if (activeOnly !== undefined) params.push(`active_only=${activeOnly}`);
    if (params.length) url += `?${params.join('&')}`;
    return this.http.get<any[]>(url);
  }
}