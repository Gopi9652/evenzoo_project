import { Injectable, NgZone, OnDestroy } from '@angular/core';
import { Subject, Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class WebsocketService implements OnDestroy {

  private socket: WebSocket | null = null;
  private messageSubject = new Subject<any>();
  private reconnectTimeout: any;

  constructor(private zone: NgZone) {}

  connect(): void {

    const token = localStorage.getItem('access_token');

    if (!token) {
      console.log('❌ No access token found');
      return;
    }

    if (
      this.socket &&
      (
        this.socket.readyState === WebSocket.OPEN ||
        this.socket.readyState === WebSocket.CONNECTING
      )
    ) {
      console.log('⚠️ WebSocket already connected or connecting');
      return;
    }

    const wsUrl = environment.apiUrl
      .replace('http', 'ws')
      .replace('/api', '');

    const fullUrl = `${wsUrl}/ws?token=${token}`;

    console.log('🔌 Connecting to:', fullUrl);

    this.socket = new WebSocket(fullUrl);

    this.socket.onopen = () => {
      console.log('✅ WebSocket connected successfully');

      this.zone.run(() => {
        // Update UI if needed
      });
    };

    this.socket.onmessage = (event) => {

      const data = JSON.parse(event.data);

      console.log('📩 WebSocket message received:', data);

      this.zone.run(() => {
        this.messageSubject.next(data);
      });
    };

    this.socket.onerror = (error) => {

      console.error('❌ WebSocket error:', error);

      this.zone.run(() => {
        this.socket?.close();
      });
    };

    this.socket.onclose = (event) => {

      console.log(
        '🔴 WebSocket closed',
        'Code:',
        event.code,
        'Reason:',
        event.reason
      );

      this.zone.run(() => {

        this.reconnectTimeout = setTimeout(() => {

          if (localStorage.getItem('access_token')) {
            console.log('🔄 Attempting WebSocket reconnect...');
            this.connect();
          }

        }, 3000);

      });
    };
  }

  disconnect(): void {

    clearTimeout(this.reconnectTimeout);

    this.socket?.close();

    this.socket = null;
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }

  onMessage(): Observable<any> {
    return this.messageSubject.asObservable();
  }

  ngOnDestroy(): void {
    this.disconnect();
  }
}