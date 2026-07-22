import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-splash',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './splash.component.html',
  styleUrl: './splash.component.scss'
})
export class SplashComponent implements OnInit, OnDestroy {
  confetti: { left: number; bg: string; delay: number; duration: number; size: number; round: boolean }[] = [];
  people = ['👰', '🤵', '💃', '🕺', '👯', '🥂', '🎊', '🎈'];
  private timer?: ReturnType<typeof setTimeout>;

  constructor(private router: Router) {}

  ngOnInit() {
    const colors = ['#e8650a', '#f5a623', '#ec4899', '#8b5cf6', '#3b82f6', '#22c55e', '#f43f5e', '#facc15'];
    for (let i = 0; i < 60; i++) {
      this.confetti.push({
        left: Math.random() * 100,
        bg: colors[Math.floor(Math.random() * colors.length)],
        delay: Math.random() * 3,
        duration: 3 + Math.random() * 2.5,
        size: 6 + Math.random() * 9,
        round: Math.random() > 0.5
      });
    }
    this.timer = setTimeout(() => this.router.navigate(['/login']), 4200);
  }

  ngOnDestroy() {
    if (this.timer) clearTimeout(this.timer);
  }
}
