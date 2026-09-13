import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export type GeolocationErrorType = 'permission_denied' | 'position_unavailable' | 'timeout' | 'not_supported';

@Injectable({ providedIn: 'root' })
export class GeolocationService {

  isSupported(): boolean {
    return 'geolocation' in navigator;
  }

  getCurrentPosition(): Observable<Coordinates> {
    return new Observable((observer) => {
      if (!this.isSupported()) {
        observer.error({ type: 'not_supported' as GeolocationErrorType, message: 'Location services are not supported on this device or browser.' });
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          observer.next({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
          observer.complete();
        },
        (error) => {
          let errorType: GeolocationErrorType = 'position_unavailable';
          let message = 'Unable to detect your location.';

          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorType = 'permission_denied';
              message = 'Location permission was denied. You can still select your city manually below.';
              break;
            case error.POSITION_UNAVAILABLE:
              errorType = 'position_unavailable';
              message = 'Your location could not be determined. Please select your city manually.';
              break;
            case error.TIMEOUT:
              errorType = 'timeout';
              message = 'Location request timed out. Please try again or select manually.';
              break;
          }

          observer.error({ type: errorType, message });
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000  // accept a cached position up to 5 minutes old
        }
      );
    });
  }
}