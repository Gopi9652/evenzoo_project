import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface State {
  id: number;
  name: string;
}

export interface City {
  id: number;
  name: string;
  state_id: number;
}

@Injectable({ providedIn: 'root' })
export class LocationService {
  private apiUrl = `${environment.apiUrl}/location`;

  constructor(private http: HttpClient) {}

  getStates(): Observable<State[]> {
    return this.http.get<State[]>(`${this.apiUrl}/states`);
  }

  getCities(stateId?: number): Observable<City[]> {
    let url = `${this.apiUrl}/cities`;
    if (stateId) url += `?state_id=${stateId}`;
    return this.http.get<City[]>(url);
  }
  getCityById(cityId: number): Observable<City> {
  return this.http.get<City>(`${this.apiUrl}/cities/${cityId}`);
}
}