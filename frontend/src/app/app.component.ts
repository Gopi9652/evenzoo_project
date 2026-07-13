import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { AuthService } from './core/services/auth.service';
import { WebsocketService } from './core/services/websocket.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  title = 'evenzoo-frontend';

  constructor(
    private authService: AuthService,
    private ws: WebsocketService
  ) {}

  ngOnInit() {
    if (this.authService.isLoggedIn()) {
      this.ws.connect();
    }
  }
}