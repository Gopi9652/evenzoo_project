import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Booking, BookingCreateRequest } from '../models/booking.model';

export interface EventType {
  id: number;
  name: string;
}

@Injectable({ providedIn: 'root' })
export class BookingService {
  private apiUrl = `${environment.apiUrl}/bookings`;

  constructor(private http: HttpClient) {}

  getEventTypes(): Observable<EventType[]> {
    return this.http.get<EventType[]>(`${this.apiUrl}/event-types`);
  }

  createBooking(data: BookingCreateRequest): Observable<Booking> {
    return this.http.post<Booking>(this.apiUrl, data);
  }

  getMyBookings(status?: string): Observable<Booking[]> {
    let url = `${this.apiUrl}/my`;
    if (status) url += `?status=${status}`;
    return this.http.get<Booking[]>(url);
  }

  getVendorBookings(status?: string): Observable<Booking[]> {
    let url = `${this.apiUrl}/vendor`;
    if (status) url += `?status=${status}`;
    return this.http.get<Booking[]>(url);
  }

  getBooking(bookingId: number): Observable<Booking> {
    return this.http.get<Booking>(`${this.apiUrl}/${bookingId}`);
  }

  updateStatus(bookingId: number, status: string, reason?: string): Observable<Booking> {
    return this.http.put<Booking>(`${this.apiUrl}/${bookingId}/status`, { status, reason });
  }

  getBookingHistory(bookingId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${bookingId}/history`);
  }
}