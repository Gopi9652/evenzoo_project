import { Component, OnInit, ViewChild, ElementRef, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-intro-splash',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './intro-splash.component.html',
  styleUrl: './intro-splash.component.scss'
})
export class IntroSplashComponent implements OnInit {
  @ViewChild('introVideo') videoRef!: ElementRef<HTMLVideoElement>;
  @Output() finished = new EventEmitter<void>();

  show = false;
  videoUrl = 'https://res.cloudinary.com/elm5helo/video/upload/v1786376307/WhatsApp_Video_2026-08-10_at_9.07.40_PM_ys6os9.mp4'; // ← replace with your real Cloudinary URL

  ngOnInit() {
    const alreadyShown = sessionStorage.getItem('evenzoo_intro_shown');

    if (alreadyShown) {
      // Already seen this session — skip straight to the app, no delay at all
      this.finished.emit();
      return;
    }

    this.show = true;
  }

  onVideoEnded() {
    this.dismiss();
  }

  onVideoError() {
    // If the video fails to load for any reason (slow connection, bad URL),
    // don't trap the user on a broken splash screen — just let them in.
    this.dismiss();
  }

  skip() {
    this.dismiss();
  }

  private dismiss() {
    sessionStorage.setItem('evenzoo_intro_shown', 'true');
    this.show = false;
    this.finished.emit();
  }
}