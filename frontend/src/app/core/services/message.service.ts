import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class MessageService {
  private apiUrl = `${environment.apiUrl}/messages`;

  constructor(private http: HttpClient) {}

  sendMessage(receiverId: number, content: string, bookingId?: number): Observable<any> {
    return this.http.post(this.apiUrl, {
      receiver_id: receiverId,
      content,
      booking_id: bookingId ?? null
    });
  }

  getConversations(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/conversations`);
  }

  getConversationByBooking(bookingId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/booking/${bookingId}`);
  }

  getConversationDirect(otherUserId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/user/${otherUserId}`);
  }
}