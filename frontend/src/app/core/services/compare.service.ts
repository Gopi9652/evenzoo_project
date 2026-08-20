import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface VendorCompareData {
  id: number;
  business_name: string;
  description?: string;
  address?: string;
  is_approved: boolean;
  avg_rating?: number;
  total_reviews: number;
  total_bookings: number;
  cover_photo_url?: string;
  services: { id: number; name: string; description?: string; price: number; price_type: string }[];
  photos: { id: number; photo_url: string; is_cover: boolean }[];
  recent_reviews: { id: number; overall_rating?: number; title?: string; body?: string }[];
  min_price?: number;
  max_price?: number;
}

@Injectable({ providedIn: 'root' })
export class CompareService {
  private apiUrl = `${environment.apiUrl}/vendors`;

  // Selected vendor IDs persist across navigation via a simple in-memory list —
  // reset on page refresh, which is fine since comparison is a short-lived task
  private selectedIds: number[] = [];

  constructor(private http: HttpClient) {}

  getSelected(): number[] {
    return [...this.selectedIds];
  }

  isSelected(vendorId: number): boolean {
    return this.selectedIds.includes(vendorId);
  }

  toggle(vendorId: number): boolean {
    const index = this.selectedIds.indexOf(vendorId);
    if (index > -1) {
      this.selectedIds.splice(index, 1);
      return false;
    } else {
      if (this.selectedIds.length >= 4) {
        return false; // caller should show a message; we refuse to add a 5th
      }
      this.selectedIds.push(vendorId);
      return true;
    }
  }

  clear(): void {
    this.selectedIds = [];
  }

  count(): number {
    return this.selectedIds.length;
  }

  compare(vendorIds: number[]): Observable<VendorCompareData[]> {
    const ids = vendorIds.join(',');
    return this.http.get<VendorCompareData[]>(`${this.apiUrl}/compare?ids=${ids}`);
  }
}