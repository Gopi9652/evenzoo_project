import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GoogleMapsModule } from '@angular/google-maps';
import { VendorService } from '../../../core/services/vendor.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { Router } from '@angular/router';
import { MatFormField } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
@Component({
  selector: 'app-nearby-vendors',
  standalone: true,
  imports: [CommonModule, GoogleMapsModule, NavbarComponent, MatIconModule],
  templateUrl: './nearby-vendors.component.html',
  styleUrl: './nearby-vendors.component.scss'
})
export class NearbyVendorsComponent implements OnInit {
  center: google.maps.LatLngLiteral = { lat: 17.4483, lng: 78.3915 };
  zoom = 12;
  vendors: any[] = [];
  selectedVendor: any = null;
  loading = true;
  locationGranted = false;

  constructor(private vendorService: VendorService, private router: Router) {}

  ngOnInit() {
    if (!navigator.geolocation) {
      this.loading = false;
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        this.center = { lat: position.coords.latitude, lng: position.coords.longitude };
        this.locationGranted = true;
        this.loadNearby();
      },
      () => {
        this.loading = false; // user declined — show a manual prompt instead
      }
    );
  }

  loadNearby() {
    this.loading = true;
    this.vendorService.getNearbyVendors(this.center.lat, this.center.lng, 25).subscribe({
      next: (data) => {
        this.vendors = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  selectVendor(vendor: any) {
    this.selectedVendor = vendor;
    this.center = { lat: vendor.latitude, lng: vendor.longitude };
    this.zoom = 15;
  }

  viewProfile(vendor: any) {
    this.router.navigate(['/browse/vendor', vendor.slug || vendor.id]);
  }
}