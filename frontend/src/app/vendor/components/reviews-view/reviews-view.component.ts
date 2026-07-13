import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { VendorService } from '../../../core/services/vendor.service';
import { ReviewService } from '../../../core/services/review.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';

@Component({
  selector: 'app-vendor-reviews',
  standalone: true,
  imports: [CommonModule, FormsModule, MatButtonModule, MatProgressSpinnerModule, NavbarComponent],
  templateUrl: './reviews-view.component.html',
  styleUrl: './reviews-view.component.scss'
})
export class ReviewsViewComponent implements OnInit {
  reviews: any[] = [];
  loading = true;
  replyDrafts: Record<number, string> = {};

  constructor(
    private vendorService: VendorService,
    private reviewService: ReviewService
  ) {}

  ngOnInit() {
    this.vendorService.getMyProfile().subscribe({
      next: (profile) => {
        this.reviewService.getVendorReviews(profile.id).subscribe({
          next: (data) => {
            this.reviews = data;
            this.loading = false;
          },
          error: () => this.loading = false
        });
      },
      error: () => this.loading = false
    });
  }

  submitReply(review: any) {
    const reply = this.replyDrafts[review.id];
    if (!reply || !reply.trim()) return;

    this.reviewService.updateReview; // not used here, reply uses dedicated endpoint
    // Use the reply-specific router endpoint from Week 6
    this.vendorService['http'] // fallback if needed
    this.replyToReview(review.id, reply);
  }

  private replyToReview(reviewId: number, reply: string) {
    const url = `${(this.reviewService as any).apiUrl}/${reviewId}/reply`;
    (this.reviewService as any).http.put(url, { vendor_reply: reply }).subscribe({
      next: () => {
        const review = this.reviews.find(r => r.id === reviewId);
        if (review) {
          review.vendor_reply = reply;
          review.vendor_reply_at = new Date().toISOString();
        }
        this.replyDrafts[reviewId] = '';
      },
      error: (err: any) => alert(err.error?.detail || 'Failed to submit reply')
    });
  }

  get avgRating(): number {
    if (this.reviews.length === 0) return 0;
    const sum = this.reviews.reduce((acc, r) => acc + Number(r.overall_rating), 0);
    return Math.round((sum / this.reviews.length) * 10) / 10;
  }
}