
import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { VendorProfile } from '../../../core/models/vendor.model';
import { CompareService } from '../../../core/services/compare.service';
import { WishlistService } from '../../../core/services/wishlist.service';

@Component({
  selector: 'app-vendor-card',
  standalone: true,
  imports: [CommonModule, RouterLink, MatIconModule, MatCheckboxModule],
  templateUrl: './vendor-card.component.html',
  styleUrl: './vendor-card.component.scss'
})
export class VendorCardComponent {
  @Input() vendor!: VendorProfile;
  isWishlisted = false;
  toggling = false;

  constructor(private wishlistService: WishlistService, public compareService: CompareService) {}
  ngOnInit() {
    this.wishlistService.checkWishlisted(this.vendor.id).subscribe({
      next: (res) => this.isWishlisted = res.is_wishlisted,
      error: () => this.isWishlisted = false
    });
  }
  get ratingStars(): number[] {
    const rating = Math.round(this.vendor.avg_rating || 0);
    return Array(5).fill(0).map((_, i) => i < rating ? 1 : 0);
  }

  get isSelected(): boolean {
    return this.compareService.isSelected(this.vendor.id);
  }


  toggleWishlist(event: Event) {
    event.preventDefault();
    event.stopPropagation();

    if (this.toggling) return;
    this.toggling = true;

    if (this.isWishlisted) {
      this.wishlistService.removeFromWishlist(this.vendor.id).subscribe({
        next: () => {
          this.isWishlisted = false;
          this.toggling = false;
        },
        error: () => this.toggling = false
      });
    } else {
      this.wishlistService.addToWishlist(this.vendor.id).subscribe({
        next: () => {
          this.isWishlisted = true;
          this.toggling = false;
        },
        error: () => this.toggling = false
      });
    }
  }
  onCompareToggle(event: Event) {
    event.preventDefault();
    event.stopPropagation();

    const added = this.compareService.toggle(this.vendor.id);
    if (!added && this.compareService.count() === 4) {
      alert('You can compare up to 4 vendors at a time. Remove one to add another.');
    }
  }
}