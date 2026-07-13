import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { VendorProfile, VendorService as VendorServiceModel, Category } from '../models/vendor.model';

@Injectable({ providedIn: 'root' })
export class VendorService {
  private apiUrl = `${environment.apiUrl}/vendors`;

  constructor(private http: HttpClient) {}

listVendors(
  stateId?: number,
  cityId?: number,
  categoryId?: number,
  skip = 0,
  limit = 20
): Observable<VendorProfile[]> {
  let url = `${this.apiUrl}?skip=${skip}&limit=${limit}`;
  if (stateId) url += `&state_id=${stateId}`;
  if (cityId) url += `&city_id=${cityId}`;
  if (categoryId) url += `&category_id=${categoryId}`;
  return this.http.get<VendorProfile[]>(url);
}

  getCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${this.apiUrl}/categories`);
  }

  getVendorDetail(vendorId: number): Observable<VendorProfile> {
    return this.http.get<VendorProfile>(`${this.apiUrl}/${vendorId}`);
  }

  getVendorServices(vendorId: number): Observable<VendorServiceModel[]> {
    return this.http.get<VendorServiceModel[]>(`${this.apiUrl}/${vendorId}/services`);
  }

  getVendorPhotos(vendorId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${vendorId}/photos`);
  }

  getVendorAvailability(vendorId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${vendorId}/availability`);
  }

  getMyProfile(): Observable<VendorProfile> {
    return this.http.get<VendorProfile>(`${this.apiUrl}/me/profile`);
  }

  updateMyProfile(data: Partial<VendorProfile>): Observable<VendorProfile> {
    return this.http.put<VendorProfile>(`${this.apiUrl}/me/profile`, data);
  }

  addService(data: any): Observable<VendorServiceModel> {
    return this.http.post<VendorServiceModel>(`${this.apiUrl}/me/services`, data);
  }

  updateService(serviceId: number, data: any): Observable<VendorServiceModel> {
    return this.http.put<VendorServiceModel>(`${this.apiUrl}/me/services/${serviceId}`, data);
  }

  deleteService(serviceId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/me/services/${serviceId}`);
  }

  addPhoto(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/me/photos`, data);
  }

  deletePhoto(photoId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/me/photos/${photoId}`);
  }

  setAvailability(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/me/availability`, data);
  }
  assignCategory(categoryId: number): Observable<any> {
  return this.http.post(`${this.apiUrl}/me/categories/${categoryId}`, {});
  }

  getMyCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(`${this.apiUrl}/me/categories`);
  }

  removeCategory(categoryId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/me/categories/${categoryId}`);
  }
  getMyDocuments(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/me/documents`);
  }

  deleteDocument(documentId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/me/documents/${documentId}`);
  }
  getMyAnalytics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/me/analytics`);
  }
}