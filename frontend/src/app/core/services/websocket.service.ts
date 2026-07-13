import { Injectable, NgZone, OnDestroy } from '@angular/core';
import { Subject, Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class WebsocketService implements OnDestroy {
  private socket: WebSocket | null = null;
  private messageSubject = new Subject<any>();
  private reconnectTimeout: any;

  constructor(private zone: NgZone) {}

  connect(): void {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    // Avoid opening a duplicate connection if one is already open/connecting
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const wsUrl = environment.apiUrl.replace('http', 'ws').replace('/api', '');
    this.socket = new WebSocket(`${wsUrl}/ws?token=${token}`);

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Force this back into Angular's zone so change detection actually runs
      this.zone.run(() => {
        this.messageSubject.next(data);
      });
    };

    this.socket.onclose = () => {
      this.zone.run(() => {
        this.reconnectTimeout = setTimeout(() => {
          if (localStorage.getItem('access_token')) {
            this.connect();
          }
        }, 3000);
      });
    };

    this.socket.onerror = () => {
      this.socket?.close();
    };
  }

  disconnect(): void {
    clearTimeout(this.reconnectTimeout);
    this.socket?.close();
    this.socket = null;
  }

  onMessage(): Observable<any> {
    return this.messageSubject.asObservable();
  }

  ngOnDestroy() {
    this.disconnect();
  }
}