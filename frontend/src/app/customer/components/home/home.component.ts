import { Component, OnInit, AfterViewInit, OnDestroy, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { VendorService } from '../../../core/services/vendor.service';
import { LocationService, State, City } from '../../../core/services/location.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { VendorProfile, Category } from '../../../core/models/vendor.model';
import { FooterComponent } from '../../../shared/components/footer/footer.component';
import { CompareService } from '../../../core/services/compare.service';
import { GeolocationService } from '../../../core/services/geolocation.service';
import { WishlistService } from '../../../core/services/wishlist.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatChipsModule, MatIconModule,
    MatSelectModule, MatFormFieldModule, MatProgressSpinnerModule,
    NavbarComponent, FooterComponent
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit, AfterViewInit, OnDestroy {
  vendors: VendorProfile[] = [];
  wishlistedVendorIds = new Set<number>();
  categories: Category[] = [];
  states: State[] = [];
  cities: City[] = [];

  selectedCategoryId: number | null = null;
  selectedStateId: number | null = null;
  selectedCityId: number | null = null;
  searchTerm = '';
  loading = true;

  skip = 0;
  limit = 20;
  hasMore = true;
  loadingMore = false;

  detectingLocation = false;
  locationError = '';

  // ---------- Why Evenzoo section ----------
  @ViewChild('whySection') whySection!: ElementRef<HTMLElement>;
  private observer?: IntersectionObserver;

  weekDays = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
  blanks = Array(4);                                   // Oct 1, 2026 is a Thursday
  days = Array.from({ length: 31 }, (_, i) => i + 1);
  booked = new Set([3, 4, 10, 11, 17, 18, 24, 25, 31]); // demo data
  selectedDay: number | null = null;

  eventDate = '';
  minDate = new Date().toISOString().split('T')[0];
  planMessage = 'Pick an event type and a date. We will show only vendors who are free.';
  planError = false;

  // ---------- NEW: tips section ----------
  quotes = [
    { text: 'A good vendor is not the cheapest one. It is the one who is free on your day and answers your message.', by: 'Evenzoo planning tip' },
    { text: 'Your event is one day. The memories from it last decades, so book the people who care about the details.', by: 'Evenzoo planning tip' },
    { text: 'Every great photograph begins with a clear conversation about what matters to you.', by: 'For customers' },
    { text: 'Every five-star review started as an honest promise kept on time.', by: 'For vendors' },
    { text: 'Plan early, ask clearly, confirm in writing. Then enjoy your own party.', by: 'Evenzoo planning tip' }
  ];
  quoteIndex = 0;
  quoteFading = false;
  private quoteTimer?: ReturnType<typeof setInterval>;

  activeTab: 'customer' | 'vendor' = 'customer';

  customerTips = [
    { icon: 'event_available', title: 'Lock the date first', text: 'Check who is free on your date before you compare prices. It saves days of calls.' },
    { icon: 'chat', title: 'Share your plan in chat', text: 'Guest count, venue, timings and theme. A clear brief gets you a clear quote.' },
    { icon: 'star', title: 'Read reviews and past bookings', text: 'Look at how many events a vendor has done, not only the star rating.' },
    { icon: 'assignment_turned_in', title: 'Confirm in writing', text: 'Agree on price, advance, delivery date and cancellation terms inside the chat.' }
  ];

  vendorTips = [
    { icon: 'edit_calendar', title: 'Keep your calendar current', text: 'Mark booked dates right away. Customers skip vendors whose availability looks unreliable.' },
    { icon: 'photo_library', title: 'Show your best 10 photos', text: 'Pick recent work from different event types. Quality beats quantity.' },
    { icon: 'bolt', title: 'Reply within a few hours', text: 'The first vendor to answer clearly often wins the booking.' },
    { icon: 'payments', title: 'List what is included', text: 'State hours, travel, extras and advance amount so there are no surprises later.' }
  ];

  timeline = [
    { when: '3–6 months before', what: 'Book photographer, decorator and caterer.' },
    { when: '2 months before', what: 'Finalise theme, menu and shot list.' },
    { when: '2 weeks before', what: 'Reconfirm timings and payment plan.' },
    { when: 'Event day', what: 'Share one point of contact with every vendor.' },
    { when: 'After the event', what: 'Leave an honest review to help the next family.' }
  ];

  calendarDate = new Date();

  monthNames = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
  ];

  constructor(
    private vendorService: VendorService,
    private locationService: LocationService,
    public compareService: CompareService,
    private router: Router,
    private wishlistService: WishlistService,
    private geolocationService: GeolocationService   // ← new
  ) {}

  ngOnInit() {
    this.loadCategories();
    this.loadStates();
    this.loadCities();
    this.loadVendors();
    this.loadWishlistStatus();
  }
  loadWishlistStatus(): void {

  this.wishlistService.getWishlistedVendorIds().subscribe({
    next: (res) => {

      this.wishlistedVendorIds = new Set(
        res.vendor_ids || []
      );

    },

    error: () => {

      this.wishlistedVendorIds = new Set<number>();

    }
  });
}

  ngAfterViewInit() {
    // scroll reveal for Why Evenzoo
    this.observer = new IntersectionObserver(
      entries => entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('in-view');
          this.observer?.unobserve(e.target);
        }
      }),
      { threshold: 0.15 }
    );
    this.whySection.nativeElement
      .querySelectorAll('.reveal')
      .forEach(el => this.observer!.observe(el));

    // auto-rotate quotes (skipped when the user prefers reduced motion)
    this.startQuoteTimer();
  }

  ngOnDestroy() {
    this.observer?.disconnect();
    if (this.quoteTimer) clearInterval(this.quoteTimer);
  }

  selectCategory(categoryId: number | null) {
    this.selectedCategoryId = categoryId;
  }

  checkAvailability() {
    // if (!this.selectedCategoryId || !this.eventDate) {
    //   this.planError = true;
    //   this.planMessage = 'Please choose an event type and a date first.';
    //   return;
    // }
    this.planError = false;
    this.router.navigate(['/customer/vendor-card'], {
      queryParams: { category_id: this.selectedCategoryId, date: this.eventDate }
    });
  }

  postRequirement() {
    // TODO: change to your real "post requirement" route
    this.router.navigate(['/customer/post/create']);
  }

  // ---------- NEW: quote carousel ----------
  goToQuote(i: number) {
    this.showQuote(i);
    this.startQuoteTimer();
  }

  private showQuote(i: number) {
    this.quoteFading = true;
    setTimeout(() => {
      this.quoteIndex = i;
      this.quoteFading = false;
    }, 200);
  }

  private startQuoteTimer() {
    if (this.quoteTimer) clearInterval(this.quoteTimer);
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    this.quoteTimer = setInterval(
      () => this.showQuote((this.quoteIndex + 1) % this.quotes.length),
      6000
    );
  }

  // ---------- existing logic (unchanged) ----------
  goToCompare() {
    const ids = this.compareService.getSelected();
    if (ids.length < 2) {
      alert('Select at least 2 vendors to compare');
      return;
    }
    //this.router.navigate(['/customer/compare'], { queryParams: { ids: ids.join(',') } });
    this.router.navigate(['/browse/compare'], { queryParams: { ids: ids.join(',') } });
  }

  loadCategories() {
    this.vendorService.getCategories().subscribe({
      next: (data) => this.categories = data,
      error: (err) => console.error('Failed to load categories', err)
    });
  }

  loadStates() {
    this.locationService.getStates().subscribe({
      next: (data) => this.states = data,
      error: (err) => console.error('Failed to load states', err)
    });
  }

  loadCities(stateId?: number) {
    this.locationService.getCities(stateId).subscribe({
      next: (data) => this.cities = data,
      error: (err) => console.error('Failed to load cities', err)
    });
  }

  onStateChange() {
    this.selectedCityId = null;
    this.loadCities(this.selectedStateId ?? undefined);
    this.loadVendors();
  }

  onCityChange() {
    this.loadVendors();
  }

  clearLocationFilters() {
    this.selectedStateId = null;
    this.selectedCityId = null;
    this.loadCities();
    this.loadVendors();
  }

  loadVendors(reset = true) {
    if (reset) {
      this.skip = 0;
      this.vendors = [];
      this.hasMore = true;
      this.loading = true;
    } else {
      this.loadingMore = true;
    }

    this.vendorService.listVendors(
      this.selectedStateId || undefined,
      this.selectedCityId || undefined,
      this.selectedCategoryId || undefined,
      this.skip,
      this.limit,
      undefined
    ).subscribe({
      next: (data) => {
        this.vendors = reset ? data : [...this.vendors, ...data];
        this.hasMore = data.length === this.limit;
        this.loading = false;
        this.loadingMore = false;
      },
      error: () => {
        this.loading = false;
        this.loadingMore = false;
      }
    });
  }

  loadMore() {
    this.skip += this.limit;
    this.loadVendors(false);
  }

  get filteredVendors(): VendorProfile[] {
    if (!this.searchTerm.trim()) return this.vendors;

    const term = this.normalize(this.searchTerm);

    return this.vendors
      .map(v => ({ vendor: v, score: this.matchScore(v, term) }))
      .filter(x => x.score > 0)
      .sort((a, b) => b.score - a.score)
      .map(x => x.vendor);
  }

  private normalize(text: string): string {
    return text
      .toLowerCase()
      .trim()
      .replace(/[^\w\s]/g, '')
      .replace(/\s+/g, ' ');
  }

  private matchScore(vendor: VendorProfile, term: string): number {
    const name = this.normalize(vendor.business_name || '');
    const desc = this.normalize(vendor.description || '');

    if (name === term) return 100;
    if (name.startsWith(term)) return 90;
    if (name.includes(term)) return 75;

    const termWords = term.split(' ').filter(w => w.length > 0);
    const nameWords = name.split(' ');

    let wordMatchCount = 0;
    for (const tw of termWords) {
      if (nameWords.some(nw => nw.startsWith(tw) || nw.includes(tw))) {
        wordMatchCount++;
      }
    }
    if (wordMatchCount > 0) {
      return 40 + (wordMatchCount / termWords.length) * 20;
    }

    if (desc.includes(term)) return 20;

    const descWords = desc.split(' ');
    let descWordMatchCount = 0;
    for (const tw of termWords) {
      if (descWords.some(dw => dw.startsWith(tw) || dw.includes(tw))) {
        descWordMatchCount++;
      }
    }
    if (descWordMatchCount > 0) {
      return 5 + (descWordMatchCount / termWords.length) * 10;
    }

    return 0;
  }

  useMyLocation() {
    this.detectingLocation = true;
    this.locationError = '';

    this.geolocationService.getCurrentPosition().subscribe({
      next: (coords) => {
        this.locationService.findNearestCity(coords.latitude, coords.longitude).subscribe({
          next: (nearest) => {
            this.detectingLocation = false;
            this.selectedStateId = nearest.state_id;
            this.loadCities(nearest.state_id);
            this.selectedCityId = nearest.city_id;
            this.loadVendors();
          },
          error: () => {
            this.detectingLocation = false;
            this.locationError = 'Could not match your location to a supported city.';
          }
        });
      },
      error: (err) => {
        this.detectingLocation = false;
        this.locationError = err.message;
      }
    });
  }

  pickDay(d: number) {
    this.selectedDay = d;

    const year = this.calendarDate.getFullYear();
    const month = this.calendarDate.getMonth() + 1;

    this.eventDate =
      `${year}-${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`;

    console.log('Selected day:', this.selectedDay);
    console.log('Selected date:', this.eventDate);
  }
}