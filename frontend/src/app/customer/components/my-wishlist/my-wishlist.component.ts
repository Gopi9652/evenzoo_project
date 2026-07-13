import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { WishlistService, WishlistVendor } from '../../../core/services/wishlist.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';

@Component({
  selector: 'app-my-wishlist',
  standalone: true,
  imports: [
    CommonModule, RouterLink, MatIconModule,
    MatButtonModule, MatProgressSpinnerModule, NavbarComponent
  ],
  templateUrl: './my-wishlist.component.html',
  styleUrl: './my-wishlist.component.scss'
})
export class MyWishlistComponent implements OnInit {
  items: WishlistVendor[] = [];
  loading = true;
  removingId: number | null = null;

  constructor(private wishlistService: WishlistService) {}

  ngOnInit() {
    this.loadWishlist();
  }

  loadWishlist() {
    this.loading = true;
    this.wishlistService.getMyWishlist().subscribe({
      next: (data) => {
        this.items = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  remove(vendorId: number) {
    this.removingId = vendorId;
    this.wishlistService.removeFromWishlist(vendorId).subscribe({
      next: () => {
        this.items = this.items.filter(i => i.vendor_id !== vendorId);
        this.removingId = null;
      },
      error: () => this.removingId = null
    });
  }
}