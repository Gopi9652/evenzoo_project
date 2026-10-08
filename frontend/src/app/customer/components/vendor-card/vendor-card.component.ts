import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, ActivatedRoute } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { VendorProfile } from '../../../core/models/vendor.model';
import { CompareService } from '../../../core/services/compare.service';
import { WishlistService } from '../../../core/services/wishlist.service';
import { VendorService } from '../../../core/services/vendor.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { LocationService, State, City } from '../../../core/services/location.service';
import { FormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { FooterComponent } from '../../../shared/components/footer/footer.component';


@Component({
  selector: 'app-vendor-card',
  standalone: true,
  imports: [
    CommonModule, RouterLink, MatIconModule, MatCheckboxModule,
    MatButtonModule, MatProgressSpinnerModule, NavbarComponent, FormsModule, MatSelectModule , FooterComponent
  ],
  templateUrl: './vendor-card.component.html',
  styleUrl: './vendor-card.component.scss'
})
export class VendorCardComponent {
  vendors: VendorProfile[] = [];
  loading = false;
  wishlistedIds = new Set<number>();
  togglingId: number | null = null;
  category_id?: number;
  date?: string;

  skip = 0;
  limit = 20;
  hasMore = true;
  loadingMore = false;

  states: State[] = [];
  cities: City[] = [];

  selectedStateId: number | null = null;
  selectedCityId: number | null = null;
  searchTerm = '';

  constructor(
    private wishlistService: WishlistService,
    public compareService: CompareService,
    private route: ActivatedRoute,
    private vendorService: VendorService,
    private locationService: LocationService
  ) {}

  ngOnInit() {
    this.loadStates();
    this.loadCities();
    this.route.queryParams.subscribe(params => {
      this.category_id = params['category_id'];
      this.date = params['date'];
      console.log("Type", this.category_id, "Date", this.date);
      this.loadVendors();   // reload whenever the filters change
    });
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

    this.vendorService.listVendors(this.selectedStateId || undefined, this.selectedCityId || undefined, this.category_id!, this.skip, this.limit, this.date).subscribe({
      next: (data) => {
        this.vendors = reset ? data : [...this.vendors, ...data];
        this.hasMore = data.length === this.limit;
        this.loading = false;
        this.loadingMore = false;
        this.loadWishlistStatus();
      },
      error: () => {
        console.error('error');
        this.vendors = [];
        this.loading = false;
        this.loadingMore = false;
      }
    });
  }

  loadMore() {
    this.skip += this.limit;
    this.loadVendors(false);
  }

  private loadWishlistStatus() {
    this.wishlistedIds.clear();
    this.vendors.forEach(v => {
      this.wishlistService.checkWishlisted(v.id).subscribe({
        next: (res) => { if (res.is_wishlisted) this.wishlistedIds.add(v.id); },
        error: () => {}
      });
    });
  }

  isWishlisted(v: VendorProfile): boolean {
    return this.wishlistedIds.has(v.id);
  }

  isSelected(v: VendorProfile): boolean {
    return this.compareService.isSelected(v.id);
  }

  getStars(v: VendorProfile): number[] {
    const rating = Math.round(v.avg_rating || 0);
    return Array(5).fill(0).map((_, i) => i < rating ? 1 : 0);
  }

  toggleWishlist(event: Event, v: VendorProfile) {
    event.preventDefault();
    event.stopPropagation();

    if (this.togglingId !== null) return;
    this.togglingId = v.id;

    if (this.isWishlisted(v)) {
      this.wishlistService.removeFromWishlist(v.id).subscribe({
        next: () => {
          this.wishlistedIds.delete(v.id);
          this.togglingId = null;
        },
        error: () => this.togglingId = null
      });
    } else {
      this.wishlistService.addToWishlist(v.id).subscribe({
        next: () => {
          this.wishlistedIds.add(v.id);
          this.togglingId = null;
        },
        error: () => this.togglingId = null
      });
    }
  }

  onCompareToggle(event: Event, v: VendorProfile) {
    event.preventDefault();
    event.stopPropagation();

    const added = this.compareService.toggle(v.id);
    if (!added && this.compareService.count() === 4) {
      alert('You can compare up to 4 vendors at a time. Remove one to add another.');
    }
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

  onCityChange() {
    this.loadVendors();
  }

  onStateChange() {
    // Reset city since the previously picked city may not belong to the new state
    this.selectedCityId = null;
    this.loadCities(this.selectedStateId ?? undefined);
    this.loadVendors();
  }

  clearLocationFilters() {
    this.selectedStateId = null;
    this.selectedCityId = null;
    this.loadCities();
    this.loadVendors();
  }
}