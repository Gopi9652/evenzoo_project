import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface CreateOrderResponse {
  order_id: string;
  amount: number;
  currency: string;
  key_id: string;
  booking_ref: string;
}

export interface PaymentStatus {
  id: number;
  booking_id: number;
  razorpay_order_id?: string;
  razorpay_payment_id?: string;
  amount: number;
  currency: string;
  status: string;
  payment_method?: string;
  paid_at?: string;
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class PaymentService {
  private apiUrl = `${environment.apiUrl}/payments`;

  constructor(private http: HttpClient) {}

  createOrder(bookingId: number): Observable<CreateOrderResponse> {
    return this.http.post<CreateOrderResponse>(`${this.apiUrl}/create-order`, {
      booking_id: bookingId
    });
  }

  verifyPayment(data: {
    booking_id: number;
    razorpay_order_id: string;
    razorpay_payment_id: string;
    razorpay_signature: string;
  }): Observable<any> {
    return this.http.post(`${this.apiUrl}/verify`, data);
  }

  getPaymentStatus(bookingId: number): Observable<PaymentStatus> {
    return this.http.get<PaymentStatus>(`${this.apiUrl}/${bookingId}`);
  }
}