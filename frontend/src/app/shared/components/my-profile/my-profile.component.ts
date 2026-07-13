import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../../../core/services/auth.service';
import { NavbarComponent } from '../navbar/navbar.component';
import { User } from '../../../core/models/user.model';

@Component({
  selector: 'app-my-profile',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule, NavbarComponent],
  templateUrl: './my-profile.component.html',
  styleUrl: './my-profile.component.scss'
})
export class MyProfileComponent implements OnInit {
  user: User | null = null;
  uploading = false;
  loading = true;

  constructor(private authService: AuthService) {}

  ngOnInit() {
    this.authService.getMe().subscribe({
      next: (data) => {
        this.user = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  get initial(): string {
    return this.user?.name?.charAt(0).toUpperCase() || 'U';
  }

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      alert('Image must be under 5MB');
      return;
    }

    this.uploading = true;
    this.authService.uploadAvatar(file).subscribe({
      next: (response) => {
        this.uploading = false;
        if (this.user) this.user.profile_photo = response.profile_photo;
      },
      error: (err) => {
        this.uploading = false;
        alert(err.error?.detail || 'Upload failed');
      }
    });
  }
}