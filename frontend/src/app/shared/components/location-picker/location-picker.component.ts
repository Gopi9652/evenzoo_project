import { CommonModule } from '@angular/common';
import { GoogleMapsModule } from '@angular/google-maps';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
export interface PickedLocation {
  latitude: number;
  longitude: number;
  address: string;
  place_id?: string;
}
@Component({
  selector: 'app-location-picker',
  standalone: true,
  imports: [CommonModule, GoogleMapsModule, MatButtonModule, MatIconModule],
  templateUrl: './location-picker.component.html',
  styleUrl: './location-picker.component.scss'
})
export class LocationPickerComponent implements OnInit, OnChanges {
  @Input() initialLat = 17.4483;
  @Input() initialLng = 78.3915;
  @Output() locationPicked = new EventEmitter<PickedLocation>();

  zoom = 13;
  center: google.maps.LatLngLiteral = { lat: this.initialLat, lng: this.initialLng };
  markerPosition: google.maps.LatLngLiteral = { lat: this.initialLat, lng: this.initialLng };
  address = '';
  loadingLocation = false;
  private hasReceivedRealLocation = false;

  ngOnInit() {
    this.center = { lat: this.initialLat, lng: this.initialLng };
    this.markerPosition = { ...this.center };
  }

  ngOnChanges(changes: SimpleChanges) {
    if ((changes['initialLat'] || changes['initialLng']) && !this.hasReceivedRealLocation) {
      this.center = { lat: this.initialLat, lng: this.initialLng };
      this.markerPosition = { ...this.center };
      this.hasReceivedRealLocation = true;
    }
  }

  onMapClick(event: google.maps.MapMouseEvent) {
    if (!event.latLng) return;
    const lat = event.latLng.lat();
    const lng = event.latLng.lng();
    this.markerPosition = { lat, lng };
    this.reverseGeocode(lat, lng);
  }

  reverseGeocode(lat: number, lng: number) {
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ location: { lat, lng } }, (results, status) => {
      if (status === 'OK' && results && results.length > 0) {
        this.address = results[0].formatted_address;
        this.locationPicked.emit({
          latitude: lat,
          longitude: lng,
          address: this.address,
          place_id: results[0].place_id
        });
      }
    });
  }

  useCurrentLocation() {
    if (!navigator.geolocation) {
      alert('Location is not supported by your browser.');
      return;
    }

    this.loadingLocation = true;
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        this.center = { lat, lng };
        this.markerPosition = { lat, lng };
        this.zoom = 15;
        this.loadingLocation = false;
        this.reverseGeocode(lat, lng);
      },
      (error) => {
        this.loadingLocation = false;
        console.error(error);
        alert('Unable to get your current location. You can still click the map to set it manually.');
      }
    );
  }
}