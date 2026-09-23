import { Component, Input, Output, EventEmitter, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-photo-lightbox',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  templateUrl: './photo-lightbox.component.html',
  styleUrl: './photo-lightbox.component.scss'
})
export class PhotoLightboxComponent {
  @Input() photos: { photo_url: string; caption?: string }[] = [];
  @Input() startIndex = 0;
  @Output() closed = new EventEmitter<void>();

  currentIndex = 0;

  ngOnChanges() {
    this.currentIndex = this.startIndex;
  }

  close() {
    this.closed.emit();
  }

  next(event?: Event) {
    event?.stopPropagation();
    if (this.currentIndex < this.photos.length - 1) {
      this.currentIndex++;
    }
  }

  prev(event?: Event) {
    event?.stopPropagation();
    if (this.currentIndex > 0) {
      this.currentIndex--;
    }
  }

  goTo(index: number, event?: Event) {
    event?.stopPropagation();
    this.currentIndex = index;
  }

  @HostListener('document:keydown', ['$event'])
  handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') this.close();
    if (event.key === 'ArrowRight') this.next();
    if (event.key === 'ArrowLeft') this.prev();
  }
}