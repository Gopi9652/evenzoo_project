import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CompareService, VendorCompareData } from '../../../core/services/compare.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';

@Component({
  selector: 'app-vendor-compare',
  standalone: true,
  imports: [CommonModule, RouterLink, MatIconModule, MatButtonModule, MatProgressSpinnerModule, NavbarComponent],
  templateUrl: './vendor-compare.component.html',
  styleUrl: './vendor-compare.component.scss'
})
export class VendorCompareComponent implements OnInit {
  vendors: VendorCompareData[] = [];
  loading = true;
  errorMessage = '';

  // Union of every service name across all compared vendors, used to build
  // aligned comparison rows even when vendors offer different service sets
  allServiceNames: string[] = [];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private compareService: CompareService
  ) {}

  ngOnInit() {
    const idsParam = this.route.snapshot.queryParamMap.get('ids');
    if (!idsParam) {
      this.errorMessage = 'No vendors selected for comparison';
      this.loading = false;
      return;
    }

    const ids = idsParam.split(',').map(Number).filter(n => !isNaN(n));

    this.compareService.compare(ids).subscribe({
      next: (data) => {
        this.vendors = data;
        this.buildServiceNameUnion();
        this.loading = false;
      },
      error: (err) => {
        this.errorMessage = err.error?.detail || 'Failed to load comparison';
        this.loading = false;
      }
    });
  }

  buildServiceNameUnion() {
    const names = new Set<string>();
    this.vendors.forEach(v => v.services.forEach(s => names.add(s.name)));
    this.allServiceNames = Array.from(names);
  }

  getServicePrice(vendor: VendorCompareData, serviceName: string): number | null {
    const match = vendor.services.find(s => s.name === serviceName);
    return match ? match.price : null;
  }

  ratingStars(rating?: number): number[] {
    const r = Math.round(rating || 0);
    return Array(5).fill(0).map((_, i) => i < r ? 1 : 0);
  }

  removeVendor(vendorId: number) {
    const remaining = this.vendors.filter(v => v.id !== vendorId).map(v => v.id);
    if (remaining.length < 2) {
      this.router.navigate(['/customer/home']);
      return;
    }
    this.router.navigate(['/customer/compare'], { queryParams: { ids: remaining.join(',') } });
  }

  get gridColumns(): string {
    return `220px repeat(${this.vendors.length}, minmax(220px, 1fr))`;
  }
}