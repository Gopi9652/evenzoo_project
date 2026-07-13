import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ReviewService } from '../../../core/services/review.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';

@Component({
  selector: 'app-my-reviews',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatButtonModule, MatIconModule,
    MatProgressSpinnerModule, NavbarComponent
  ],
  templateUrl: './my-reviews.component.html',
  styleUrl: './my-reviews.component.scss'
})
export class MyReviewsComponent implements OnInit {
  reviews: any[] = [];
  loading = true;
  editingId: number | null = null;
  editDrafts: Record<number, any> = {};

  constructor(
    private reviewService: ReviewService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadReviews();
  }

  loadReviews() {
    this.loading = true;
    this.reviewService.getMyReviews().subscribe({
      next: (data) => {
        this.reviews = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  startEdit(review: any) {
    this.editingId = review.id;
    this.editDrafts[review.id] = {
      quality_rating: review.quality_rating,
      price_rating: review.price_rating,
      service_rating: review.service_rating,
      title: review.title,
      body: review.body
    };
  }

  cancelEdit() {
    this.editingId = null;
  }

  saveEdit(review: any) {
    const draft = this.editDrafts[review.id];
    this.reviewService.updateReview(review.id, draft).subscribe({
      next: () => {
        this.editingId = null;
        this.loadReviews();
      },
      error: (err) => alert(err.error?.detail || 'Failed to update review')
    });
  }

  deleteReview(review: any) {
    if (!confirm('Delete this review permanently?')) return;

    this.reviewService.deleteReview(review.id).subscribe({
      next: () => this.loadReviews(),
      error: (err) => alert(err.error?.detail || 'Failed to delete review')
    });
  }

  viewBooking(bookingId: number) {
    this.router.navigate(['/customer/booking', bookingId]);
  }
}