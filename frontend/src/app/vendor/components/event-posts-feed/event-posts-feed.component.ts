import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { EventPostService } from '../../../core/services/event-post.service';
import { LocationService, State, City } from '../../../core/services/location.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { EventPost } from '../../../core/models/event-post.model';
import { ActivatedRoute } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { SendQuoteDialogComponent } from '../../../shared/components/send-quote-dialog/send-quote-dialog.component';
import { VendorService } from '../../../core/services/vendor.service';
export interface Category {
  id: number;
  name: string;
  description?: string;
  icon?: string;
}
@Component({
  selector: 'app-event-posts-feed',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatSelectModule, MatFormFieldModule,
    MatButtonModule, MatProgressSpinnerModule, NavbarComponent
  ],
  templateUrl: './event-posts-feed.component.html',
  styleUrl: './event-posts-feed.component.scss'
})
export class EventPostsFeedComponent implements OnInit {
  posts: EventPost[] = [];
  states: State[] = [];
  cities: City[] = [];
  filterStateId: number | null = null;
  filterCityId: number | null = null;
  highlightPostId: number | null = null;
  loading = true;
  categories: Category[] = [];
  selectedEventTypeId: number | null = null;

  isFiltering = false;   // tracks whether vendor has actively chosen to look outside their own area

  constructor(
    private eventPostService: EventPostService,
    private locationService: LocationService,
    private router: Router,
    private route: ActivatedRoute,
    private dialog: MatDialog,
    private vendorService:VendorService
  ) {}

  ngOnInit() {
    this.vendorService.getCategories().subscribe({ next: (data:any) => this.categories = data });
    this.route.queryParams.subscribe(params => {
      this.highlightPostId = params['highlight'] ? Number(params['highlight']) : null;
    });
    this.locationService.getStates().subscribe({ next: (data) => this.states = data });
    this.locationService.getCities().subscribe({ next: (data) => this.cities = data });
    this.loadFeed();
  }



  onStateFilterChange() {
    this.filterCityId = null;
    if (this.filterStateId) {
      this.locationService.getCities(this.filterStateId).subscribe({
        next: (data) => this.cities = data
      });
    } else {
      this.locationService.getCities().subscribe({ next: (data) => this.cities = data });
    }
    this.applyFilter();
  }

  onCityFilterChange() {
    this.applyFilter();
  }

  applyFilter() {
    this.isFiltering = !!(this.filterStateId || this.filterCityId);
    this.loadFeed();
  }

  clearFilter() {
    this.filterStateId = null;
    this.filterCityId = null;
    this.isFiltering = false;
    this.locationService.getCities().subscribe({ next: (data) => this.cities = data });
    this.loadFeed();
  }

  messageCustomer(post: EventPost) {
    this.router.navigate(['/chat/user', post.customer_id], {
      queryParams: { name: post.customer_name || 'Customer' }
    });
  }
sendQuote(post: EventPost) {
  console.log('Post items:', post.items);   // ← temporary debug line
  const dialogRef = this.dialog.open(SendQuoteDialogComponent, {
    width: '460px',
    data: {
      eventPostId: post.id,
      customerName: post.customer_name,
      items: post.items?.map(i => ({ category_id: i.category_id, category_name: i.category_name })),
      singleCategoryId: post.category_id,
      singleCategoryName: post.category_name
    }
  });
  dialogRef.afterClosed().subscribe(result => {
    if (result === 'success') {
      alert('Quote sent to the customer!');
      this.loadFeed();
    }
  });
}
  onEventTypeChange() {
    this.loadFeed();
  }

  loadFeed() {
    this.loading = true;
    this.eventPostService.getVendorFeed(
      this.filterStateId || undefined,
      this.filterCityId || undefined,
      this.selectedEventTypeId || undefined   // pass through as event_type_id
    ).subscribe({
      next: (data) => { this.posts = data; this.loading = false; },
      error: () => this.loading = false
    });
  }
}