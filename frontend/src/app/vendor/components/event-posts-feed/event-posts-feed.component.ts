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
  isFiltering = false;   // tracks whether vendor has actively chosen to look outside their own area

  constructor(
    private eventPostService: EventPostService,
    private locationService: LocationService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.highlightPostId = params['highlight'] ? Number(params['highlight']) : null;
    });
    this.locationService.getStates().subscribe({ next: (data) => this.states = data });
    this.locationService.getCities().subscribe({ next: (data) => this.cities = data });
    this.loadFeed();
  }

  loadFeed() {
    this.loading = true;
    this.eventPostService.getVendorFeed(
      this.filterStateId || undefined,
      this.filterCityId || undefined
    ).subscribe({
      next: (data) => {
        this.posts = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
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
}