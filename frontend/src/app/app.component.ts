import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from './core/services/auth.service';
import { WebsocketService } from './core/services/websocket.service';
import { CookieConsentComponent } from './shared/components/cookie-consent/cookie-consent.component';
import { IntroSplashComponent } from './shared/components/intro-splash/intro-splash.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule, RouterOutlet,
    CookieConsentComponent, IntroSplashComponent
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  title = 'evenzoo-frontend';
  introFinished = false;

  constructor(
    private authService: AuthService,
    private ws: WebsocketService
  ) {}

  ngOnInit() {
    if (this.authService.isLoggedIn()) {
      this.ws.connect();
    }
  }

  onIntroFinished() {
    this.introFinished = true;
  }
}