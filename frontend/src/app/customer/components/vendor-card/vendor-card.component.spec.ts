import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { VendorProfile } from '../../../core/models/vendor.model';

@Component({
  selector: 'app-vendor-card',
  standalone: true,
  imports: [CommonModule, RouterLink, MatIconModule],
  templateUrl: './vendor-card.component.html',
  styleUrl: './vendor-card.component.scss'
})
export class VendorCardComponent {
  @Input() vendor!: VendorProfile;

  get ratingStars(): number[] {
    const rating = Math.round(this.vendor.avg_rating || 0);
    return Array(5).fill(0).map((_, i) => i < rating ? 1 : 0);
  }
}