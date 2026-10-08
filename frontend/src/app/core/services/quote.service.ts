import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Quote {
  id: number;
  event_post_id?: number;
  vendor_id: number;
  vendor_business_name?: string;
  vendor_avg_rating?: number;
  customer_id: number;
  customer_name?: string;
  category_id?: number;
  category_name?: string;
  quoted_amount?: number;
  message?: string;
  status: string;
  requested_by: string;
  created_at: string;
  vendor_slug?: string;
  responded_at?:string;
}

@Injectable({ providedIn: 'root' })
export class QuoteService {
  private apiUrl = `${environment.apiUrl}/quotes`;

  constructor(private http: HttpClient) {}

  requestQuote(vendorId: number, eventPostId?: number, categoryId?: number, message?: string): Observable<Quote> {
    return this.http.post<Quote>(`${this.apiUrl}/request`, {
      vendor_id: vendorId,
      event_post_id: eventPostId,
      category_id: categoryId,
      message
    });
  }

  respondToQuote(quoteId: number, quotedAmount: number, message?: string): Observable<Quote> {
    return this.http.put<Quote>(`${this.apiUrl}/${quoteId}/respond`, {
      quoted_amount: quotedAmount,
      message
    });
  }

  updateStatus(quoteId: number, status: 'accepted' | 'declined' | 'withdrawn'): Observable<Quote> {
    return this.http.put<Quote>(`${this.apiUrl}/${quoteId}/status`, { status });
  }

  getMyQuotes(categoryId?: number, eventPostId?: number, days = 30, fromDate?: string, toDate?: string): Observable<Quote[]> {
    let url = `${this.apiUrl}/my`;
    const params: string[] = [];
    if (categoryId) params.push(`category_id=${categoryId}`);
    if (eventPostId) params.push(`event_post_id=${eventPostId}`);
    if (fromDate) { params.push(`from_date=${fromDate}`); }
    else { params.push(`days=${days}`); }
    if (toDate) params.push(`to_date=${toDate}`);
    if (params.length) url += `?${params.join('&')}`;
    return this.http.get<Quote[]>(url);
  }

  getVendorReceivedQuotes(categoryId?: number, days = 30, fromDate?: string, toDate?: string): Observable<Quote[]> {
    let url = `${this.apiUrl}/vendor-received`;
    const params: string[] = [];
    if (categoryId) params.push(`category_id=${categoryId}`);
    if (fromDate) { params.push(`from_date=${fromDate}`); }
    else { params.push(`days=${days}`); }
    if (toDate) params.push(`to_date=${toDate}`);
    if (params.length) url += `?${params.join('&')}`;
    return this.http.get<Quote[]>(url);
  }

  getQuoteSummaryByPost(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/my/summary-by-post`);
  }


 offerQuoteDirect(eventPostId: number, categoryId: number | null, quotedAmount: number, message?: string): Observable<Quote> {
  return this.http.post<Quote>(`${this.apiUrl}/offer-direct`, {
    event_post_id: eventPostId,
    category_id: categoryId,
    quoted_amount: quotedAmount,
    message
  });
}
offerBundleQuote(eventPostId: number, items: { category_id: number; quoted_amount: number }[], message?: string): Observable<Quote[]> {
  return this.http.post<Quote[]>(`${this.apiUrl}/offer-bundle`, {
    event_post_id: eventPostId,
    items,
    message
  });
}
}