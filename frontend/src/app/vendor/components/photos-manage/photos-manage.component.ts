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
  videos: any[] = [];
  uploadingVideo = false;

  constructor(
    private vendorService: VendorService,
    private http: HttpClient
  ) {}

  ngOnInit() {
    this.vendorService.getMyProfile().subscribe({
      next: (profile) => {
        this.vendorId = profile.id;
        this.loadPhotos();
        this.loadVideos();
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
  loadVideos() {
  this.vendorService.getVendorVideos(this.vendorId).subscribe({
    next: (data) => this.videos = data
  });
}

onVideoSelected(event: any) {
  const file: File = event.target.files[0];
  if (!file) return;

  if (!file.type.startsWith('video/')) {
    alert('Please select a video file');
    return;
  }
  if (file.size > 50 * 1024 * 1024) {
    alert('Video must be under 50MB — larger files will be automatically compressed, but we cap uploads at 50MB.');
    return;
  }

  this.uploadingVideo = true;
  this.vendorService.uploadVideo(file).subscribe({
    next: () => {
      this.uploadingVideo = false;
      this.loadVideos();
    },
    error: (err) => {
      this.uploadingVideo = false;
      alert(err.error?.detail || 'Video upload failed');
    }
  });
}

deleteVideo(videoId: number) {
  if (!confirm('Delete this video?')) return;
  this.vendorService.deleteVideo(videoId).subscribe({
    next: () => this.loadVideos(),
    error: (err) => alert(err.error?.detail || 'Failed to delete video')
  });
}
}