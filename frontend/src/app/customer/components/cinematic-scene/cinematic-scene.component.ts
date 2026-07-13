import {
  Component, Input, OnInit, OnDestroy,
  ElementRef, ViewChild, AfterViewInit
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { CinematicScene } from '../../../core/models/scene.model';

@Component({
  selector: 'app-cinematic-scene',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './cinematic-scene.component.html',
  styleUrl: './cinematic-scene.component.scss'
})
export class CinematicSceneComponent implements OnInit, AfterViewInit, OnDestroy {
  @Input() scenes: CinematicScene[] = [];

  activeKey = '';
  private observer?: IntersectionObserver;

  @ViewChild('scrimVideo') scrimVideo?: ElementRef<HTMLVideoElement>;

  ngOnInit() {
    if (this.scenes.length) {
      this.activeKey = this.scenes[0].key;
    }
  }

  ngAfterViewInit() {
    // Wait a tick for section elements (owned by the parent page) to exist in the DOM
    setTimeout(() => this.observeSections(), 0);
  }

  private observeSections() {
    const options: IntersectionObserverInit = { threshold: 0.5 };

    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const key = entry.target.getAttribute('data-scene-key');
          if (key) {
            this.activeKey = key;
            this.playActiveVideoIfAny();
          }
        }
      });
    }, options);

    this.scenes.forEach(scene => {
      const el = document.getElementById(scene.sectionId);
      if (el) this.observer!.observe(el);
    });
  }

  private playActiveVideoIfAny() {
    // Play only the currently-active video; pause everything else to save resources/battery
    const videos = document.querySelectorAll<HTMLVideoElement>('.cine-scene video');
    videos.forEach(v => {
      const key = v.closest('.cine-scene')?.getAttribute('data-key');
      if (key === this.activeKey) {
        v.play().catch(() => {}); // ignore autoplay-block errors silently
      } else {
        v.pause();
      }
    });
  }

  isActive(key: string): boolean {
    return key === this.activeKey;
  }

  scrollTo(sectionId: string) {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' });
  }

  ngOnDestroy() {
    this.observer?.disconnect();
  }
}