import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import {
  Component,
  Input,
  Output,
  EventEmitter,
  OnInit,
  OnChanges,
  SimpleChanges,
  AfterViewInit,
  OnDestroy
} from '@angular/core';

import * as L from 'leaflet';

export interface PickedLocation {
  latitude: number;
  longitude: number;
  address: string;
  place_id?: string;
}

@Component({
  selector: 'app-location-picker',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './location-picker.component.html',
  styleUrl: './location-picker.component.scss'
})
export class LocationPickerComponent
  implements OnInit, AfterViewInit, OnChanges, OnDestroy {

  @Input() initialLat: number = 17.4483;
  @Input() initialLng: number = 78.3915;

  @Output() locationPicked =
    new EventEmitter<PickedLocation>();

  zoom: number = 13;

  address: string = '';

  loadingLocation: boolean = false;

  private map!: L.Map;

  private marker!: L.Marker;

  private mapInitialized: boolean = false;

  ngOnInit(): void {
    this.initialLat = Number(this.initialLat);
    this.initialLng = Number(this.initialLng);
  }

  ngAfterViewInit(): void {
    this.initializeMap();
  }

  ngOnChanges(changes: SimpleChanges): void {

    if (
      changes['initialLat'] ||
      changes['initialLng']
    ) {

      const lat = Number(this.initialLat);
      const lng = Number(this.initialLng);

      if (
        Number.isFinite(lat) &&
        Number.isFinite(lng)
      ) {

        if (this.mapInitialized) {
          this.updateMapLocation(lat, lng);
        }
      }
    }
  }

  private initializeMap(): void {

    const lat = Number(this.initialLat);
    const lng = Number(this.initialLng);

    if (
      !Number.isFinite(lat) ||
      !Number.isFinite(lng)
    ) {
      console.error(
        'Invalid initial location:',
        this.initialLat,
        this.initialLng
      );

      return;
    }

    this.map = L.map('location-map', {
      center: [lat, lng],
      zoom: this.zoom,
      zoomControl: true
    });

    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        maxZoom: 19,
        attribution:
          '&copy; OpenStreetMap contributors'
      }
    ).addTo(this.map);

    this.marker = L.marker(
      [lat, lng],
      {
        draggable: true
      }
    ).addTo(this.map);

    this.marker.on(
      'dragend',
      () => {

        const position =
          this.marker.getLatLng();

        this.handleLocationChange(
          position.lat,
          position.lng
        );
      }
    );

    this.map.on(
      'click',
      (event: L.LeafletMouseEvent) => {

        this.handleLocationChange(
          event.latlng.lat,
          event.latlng.lng
        );
      }
    );

    this.mapInitialized = true;

    setTimeout(() => {
      this.map.invalidateSize();
    }, 100);
  }

  private updateMapLocation(
    lat: number,
    lng: number
  ): void {

    if (!this.map || !this.marker) {
      return;
    }

    const newPosition =
      L.latLng(lat, lng);

    this.map.setView(
      newPosition,
      this.zoom
    );

    this.marker.setLatLng(
      newPosition
    );
  }

  private handleLocationChange(
    lat: number,
    lng: number
  ): void {

    this.marker.setLatLng([
      lat,
      lng
    ]);

    this.map.setView(
      [lat, lng],
      this.zoom
    );

    this.reverseGeocode(
      lat,
      lng
    );
  }

  private async reverseGeocode(
    lat: number,
    lng: number
  ): Promise<void> {

    this.address =
      'Finding address...';

    try {

      const url =
        `https://nominatim.openstreetmap.org/reverse` +
        `?format=jsonv2` +
        `&lat=${encodeURIComponent(lat)}` +
        `&lon=${encodeURIComponent(lng)}` +
        `&addressdetails=1`;

      const response =
        await fetch(url, {
          headers: {
            'Accept': 'application/json'
          }
        });

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data =
        await response.json();

      const address =
        data.display_name || '';

      this.address =
        address ||
        'Address not found';

      this.locationPicked.emit({
        latitude: lat,
        longitude: lng,
        address: address,
        place_id: data.place_id
          ? String(data.place_id)
          : undefined
      });

    } catch (error) {

      console.error(
        'Reverse geocoding failed:',
        error
      );

      this.address =
        'Unable to find address';

      this.locationPicked.emit({
        latitude: lat,
        longitude: lng,
        address: ''
      });
    }
  }

  useCurrentLocation(): void {

    if (!navigator.geolocation) {

      alert(
        'Location is not supported by your browser.'
      );

      return;
    }

    this.loadingLocation = true;

    this.address =
      'Finding your current location...';

    navigator.geolocation.getCurrentPosition(

      (position) => {

        const lat =
          position.coords.latitude;

        const lng =
          position.coords.longitude;

        console.log(
          'Current location:',
          lat,
          lng
        );

        this.updateMapLocation(
          lat,
          lng
        );

        this.zoom = 15;

        this.map.setView(
          [lat, lng],
          this.zoom
        );

        this.loadingLocation = false;

        this.reverseGeocode(
          lat,
          lng
        );
      },

      (error) => {

        this.loadingLocation = false;

        console.error(
          'Geolocation error:',
          error
        );

        switch (error.code) {

          case error.PERMISSION_DENIED:

            alert(
              'Location permission was denied. Please allow location access in your browser.'
            );

            break;

          case error.POSITION_UNAVAILABLE:

            alert(
              'Your current location is unavailable.'
            );

            break;

          case error.TIMEOUT:

            alert(
              'Getting your location timed out. Please try again.'
            );

            break;

          default:

            alert(
              'Unable to get your current location.'
            );
        }
      },

      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  }

  ngOnDestroy(): void {

    if (this.map) {
      this.map.remove();
    }
  }
}