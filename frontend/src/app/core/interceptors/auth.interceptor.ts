import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, switchMap, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const http = inject(HttpClient);

  const accessToken = localStorage.getItem('access_token');

  // Don't attach access token to refresh request
  const isRefreshRequest = req.url.includes('/auth/refresh');

  if (!accessToken || isRefreshRequest) {
    return next(req);
  }

  const authReq = req.clone({
    setHeaders: {
      Authorization: `Bearer ${accessToken}`
    }
  });

  return next(authReq).pipe(
    catchError(error => {

      // Access token expired
      if (error.status === 401) {

        const refreshToken = localStorage.getItem('refresh_token');

        // No refresh token -> user must login again
        if (!refreshToken) {
          clearSession();
          return throwError(() => error);
        }

        return http.post<{ access_token: string; token_type: string }>(
          `${environment.apiUrl}/auth/refresh`,
          {
            refresh_token: refreshToken
          }
        ).pipe(

          switchMap(response => {

            // Save new access token
            localStorage.setItem(
              'access_token',
              response.access_token
            );

            // Retry original request with new token
            const retryReq = req.clone({
              setHeaders: {
                Authorization: `Bearer ${response.access_token}`
              }
            });

            return next(retryReq);
          }),

          catchError(refreshError => {

            // Refresh token is invalid/expired/revoked
            clearSession();

            return throwError(() => refreshError);
          })
        );
      }

      return throwError(() => error);
    })
  );
};


function clearSession(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('role');
  localStorage.removeItem('user_id');
  localStorage.removeItem('name');
}
