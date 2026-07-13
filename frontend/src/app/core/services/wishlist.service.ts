import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface WishlistVendor {
  wishlist_id: number;
  vendor_id: number;
  business_name: string;
  description?: string;
  avg_rating?: number;
  total_reviews: number;
  is_approved: boolean;
  saved_at: string;
}

@Injectable({ providedIn: 'root' })
export class WishlistService {
  private apiUrl = `${environment.apiUrl}/wishlist`;

  constructor(private http: HttpClient) {}

  addToWishlist(vendorId: number): Observable<any> {
    return this.http.post(this.apiUrl, { vendor_id: vendorId });
  }

  removeFromWishlist(vendorId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${vendorId}`);
  }

  getMyWishlist(): Observable<WishlistVendor[]> {
    return this.http.get<WishlistVendor[]>(this.apiUrl);
  }

  checkWishlisted(vendorId: number): Observable<{ is_wishlisted: boolean }> {
    return this.http.get<{ is_wishlisted: boolean }>(`${this.apiUrl}/check/${vendorId}`);
  }
}