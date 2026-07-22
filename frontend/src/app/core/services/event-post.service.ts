import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { EventPost, EventPostCreateRequest } from '../models/event-post.model';

@Injectable({ providedIn: 'root' })
export class EventPostService {
  private apiUrl = `${environment.apiUrl}/event-posts`;

  constructor(private http: HttpClient) {}

  createPost(data: EventPostCreateRequest): Observable<EventPost> {
    return this.http.post<EventPost>(this.apiUrl, data);
  }

  updatePost(postId: number, data: Partial<EventPostCreateRequest>): Observable<EventPost> {
    return this.http.put<EventPost>(`${this.apiUrl}/${postId}`, data);
  }

  deletePost(postId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${postId}`);
  }

  getMyPosts(): Observable<EventPost[]> {
    return this.http.get<EventPost[]>(`${this.apiUrl}/my`);
  }

  getPostById(postId: number): Observable<EventPost> {
    return this.http.get<EventPost>(`${this.apiUrl}/${postId}`);
  }

  getVendorFeed(filterStateId?: number, filterCityId?: number, skip = 0, limit = 20): Observable<EventPost[]> {
    let url = `${this.apiUrl}/vendor-feed?skip=${skip}&limit=${limit}`;
    if (filterStateId) url += `&filter_state_id=${filterStateId}`;
    if (filterCityId) url += `&filter_city_id=${filterCityId}`;
    return this.http.get<EventPost[]>(url);
  }
}