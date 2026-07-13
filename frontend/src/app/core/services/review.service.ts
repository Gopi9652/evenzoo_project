import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ReviewService {
  private apiUrl = `${environment.apiUrl}/reviews`;

  constructor(private http: HttpClient) {}

  createReview(data: any): Observable<any> {
    return this.http.post(this.apiUrl, data);
  }

  updateReview(reviewId: number, data: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/${reviewId}`, data);
  }

  deleteReview(reviewId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${reviewId}`);
  }

  getVendorReviews(vendorId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/vendor/${vendorId}`);
  }
  getMyReviews(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/my`);
  }
}