import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { VendorService } from '../../../core/services/vendor.service';
import { ReviewService } from '../../../core/services/review.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { VendorProfile, VendorService as VendorServiceModel } from '../../../core/models/vendor.model';
import { BookingFormComponent } from '../booking-form/booking-form.component';
import { environment } from '../../../../environments/environment';
@Component({
  selector: 'app-vendor-detail',
  standalone: true,
  imports: [
    CommonModule, MatIconModule, MatButtonModule, MatTabsModule,
    MatProgressSpinnerModule, MatDialogModule, NavbarComponent
  ],
  templateUrl: './vendor-detail.component.html',
  styleUrl: './vendor-detail.component.scss'
})
export class VendorDetailComponent implements OnInit {
  vendor: VendorProfile | null = null;
  services: VendorServiceModel[] = [];
  photos: any[] = [];
  reviews: any[] = [];
  reviewsLoading = true;
  loading = true;
  vendorId!: number;
  paymentsEnabled = environment.paymentsEnabled;

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private vendorService: VendorService,
    private reviewService: ReviewService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.vendorId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadVendorData();
  }

  loadVendorData() {
    this.loading = true;

    this.vendorService.getVendorDetail(this.vendorId).subscribe({
      next: (data) => {
        this.vendor = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load vendor', err);
        this.loading = false;
      }
    });

    this.vendorService.getVendorServices(this.vendorId).subscribe({
      next: (data) => this.services = data
    });

    this.vendorService.getVendorPhotos(this.vendorId).subscribe({
      next: (data) => this.photos = data
    });

    this.reviewsLoading = true;
    this.reviewService.getVendorReviews(this.vendorId).subscribe({
      next: (data) => {
        this.reviews = data;
        this.reviewsLoading = false;
      },
      error: () => this.reviewsLoading = false
    });
  }

  get ratingStars(): number[] {
    const rating = Math.round(this.vendor?.avg_rating || 0);
    return Array(5).fill(0).map((_, i) => i < rating ? 1 : 0);
  }

  starsFor(rating: number): number[] {
    const rounded = Math.round(rating);
    return Array(5).fill(0).map((_, i) => i < rounded ? 1 : 0);
  }

  // Breakdown counts for the rating summary bar (5-star, 4-star etc.)
  get ratingBreakdown(): { star: number; count: number; percent: number }[] {
    const total = this.reviews.length;
    const breakdown = [5, 4, 3, 2, 1].map(star => {
      const count = this.reviews.filter(r => Math.round(r.overall_rating) === star).length;
      return { star, count, percent: total > 0 ? Math.round((count / total) * 100) : 0 };
    });
    return breakdown;
  }

  openBookingDialog() {
    const dialogRef = this.dialog.open(BookingFormComponent, {
      width: '520px',
      maxWidth: '95vw',
      data: {
        vendorId: this.vendorId,
        vendorName: this.vendor?.business_name,
        services: this.services
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result === 'success') {
        this.router.navigate(['/customer/bookings']);
      }
    });
  }
  get whatsappLink(): string {
    if (!this.vendor?.whatsapp_number) return '';

    // Format: strip any non-digit characters, ensure country code prefix
    let phone = this.vendor.whatsapp_number.replace(/\D/g, '');
    if (phone.length === 10) {
      phone = '91' + phone;   // assume Indian number if no country code present
    }

    const message = encodeURIComponent(
      `Hi ${this.vendor.business_name}, I found your profile on Evenzoo and I'm interested in your services.`
    );

    return `https://wa.me/${phone}?text=${message}`;
  }
}