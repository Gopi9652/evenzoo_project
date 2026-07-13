import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { VendorService } from '../../../core/services/vendor.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { environment } from '../../../../environments/environment';
import { ApprovalBannerComponent } from '../../../shared/components/approval-banner/approval-banner.component';

@Component({
  selector: 'app-photos-manage',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule, NavbarComponent, ApprovalBannerComponent],
  templateUrl: './photos-manage.component.html',
  styleUrl: './photos-manage.component.scss'
})
export class PhotosManageComponent implements OnInit {
  photos: any[] = [];
  uploading = false;
  loading = true;
  vendorId!: number;

  constructor(
    private vendorService: VendorService,
    private http: HttpClient
  ) {}

  ngOnInit() {
    this.vendorService.getMyProfile().subscribe({
      next: (profile) => {
        this.vendorId = profile.id;
        this.loadPhotos();
      }
    });
  }

  loadPhotos() {
    this.loading = true;
    this.vendorService.getVendorPhotos(this.vendorId).subscribe({
      next: (data) => {
        this.photos = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (!file) return;

    this.uploading = true;
    const formData = new FormData();
    formData.append('file', file);

    this.http.post<{ photo_url: string }>(
      `${environment.apiUrl}/vendors/me/upload-photo`,
      formData
    ).subscribe({
      next: (response) => {
        // Now save the photo record
        this.vendorService.addPhoto({
          photo_url: response.photo_url,
          is_cover: this.photos.length === 0,
          sort_order: this.photos.length
        }).subscribe({
          next: () => {
            this.uploading = false;
            this.loadPhotos();
          },
          error: () => this.uploading = false
        });
      },
      error: (err) => {
        this.uploading = false;
        alert('Upload failed: ' + (err.error?.detail || 'Unknown error'));
      }
    });
  }

  deletePhoto(photoId: number) {
    if (!confirm('Delete this photo?')) return;

    this.vendorService.deletePhoto(photoId).subscribe({
      next: () => this.loadPhotos(),
      error: (err) => alert(err.error?.detail || 'Failed to delete photo')
    });
  }
}