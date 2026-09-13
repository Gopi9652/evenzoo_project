import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { VendorService } from '../../../core/services/vendor.service';
import { LocationService, State, City } from '../../../core/services/location.service';
import { VendorCardComponent } from '../vendor-card/vendor-card.component';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { VendorProfile, Category } from '../../../core/models/vendor.model';
import { FooterComponent } from '../../../shared/components/footer/footer.component';
import { CompareService } from '../../../core/services/compare.service';
import { Router } from '@angular/router';
import { GeolocationService } from '../../../core/services/geolocation.service';
@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatChipsModule, MatIconModule,
    MatSelectModule, MatFormFieldModule, MatProgressSpinnerModule,
    VendorCardComponent, NavbarComponent, FooterComponent
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  vendors: VendorProfile[] = [];
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

  constructor(
    private vendorService: VendorService,
    private locationService: LocationService,
    public compareService: CompareService,
    private router: Router,
    private geolocationService: GeolocationService   // ← new
  ) {}

  ngOnInit() {
    this.loadCategories();
    this.loadStates();
    this.loadCities();
    this.loadVendors();
  }
  goToCompare() {
    const ids = this.compareService.getSelected();
    if (ids.length < 2) {
      alert('Select at least 2 vendors to compare');
      return;
    }
    this.router.navigate(['/customer/compare'], { queryParams: { ids: ids.join(',') } });
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
    // Reset city since the previously picked city may not belong to the new state
    this.selectedCityId = null;
    this.loadCities(this.selectedStateId ?? undefined);
    this.loadVendors();
  }

  onCityChange() {
    this.loadVendors();
  }

  selectCategory(categoryId: number | null) {
    this.selectedCategoryId = categoryId;
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
      this.limit
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

            // Auto-select the matched state and city
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
}