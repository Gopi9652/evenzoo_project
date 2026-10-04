import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../../../core/services/auth.service';
import { AccountService } from '../../../core/services/account.service';
import { NavbarComponent } from '../navbar/navbar.component';
import { User } from '../../../core/models/user.model';
import { BookingService } from '../../../core/services/booking.service';
import { DatePipe, DecimalPipe } from '@angular/common';
import { WishlistService } from '../../../core/services/wishlist.service';

@Component({
  selector: 'app-my-profile',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatButtonModule, MatIconModule,
    MatFormFieldModule, MatInputModule, MatProgressSpinnerModule, NavbarComponent, DatePipe, DecimalPipe
  ],
  templateUrl: './my-profile.component.html',
  styleUrl: './my-profile.component.scss'
})
export class MyProfileComponent implements OnInit {
  user: User | null = null;
  uploading = false;
  loading = true;

  pendingEmail: string | null = null;
  pendingPhone: string | null = null;

  showEmailForm = false;
  showPhoneForm = false;
  showPhoneOtpForm = false;

  emailForm: FormGroup;
  phoneForm: FormGroup;
  phoneOtpForm: FormGroup;

  emailSubmitting = false;
  phoneSubmitting = false;
  otpSubmitting = false;
  errorMessage = '';
  successMessage = '';

  bookingStats = {
    totalBookings: 0,
    pendingBookings: 0,
    confirmedBookings: 0,
    completedBookings: 0,
    cancelledBookings: 0,
    totalAmount: 0
  };
  upcomingBooking: any = null;
  wishList: any[] = []
  isVendor: boolean = false;

  constructor(
    private authService: AuthService,
    private accountService: AccountService,
    private fb: FormBuilder,
    private bookingService: BookingService,
    private wishlistService: WishlistService
  ) {
    this.emailForm = this.fb.group({
      new_email: ['', [Validators.required, Validators.email]],
      current_password: ['', Validators.required]
    });

    this.phoneForm = this.fb.group({
      new_phone: ['', [Validators.required, Validators.pattern(/^[6-9]\d{9}$/)]],
      current_password: ['', Validators.required]
    });

    this.phoneOtpForm = this.fb.group({
      otp_code: ['', [Validators.required, Validators.pattern(/^\d{6}$/)]]
    });
  }

  ngOnInit() {
    this.authService.getMe().subscribe({
      next: (data) => {
        this.user = data;
        // console.log("USER", this.user)
        this.isVendor = this.user.role == 'vendor'
        this.loading = false;
      },
      error: () => this.loading = false
    });

    this.loadPendingChanges();
    this.loadBookingStats();
    this.loadWishList();

  }

  loadPendingChanges() {
    this.accountService.getPendingChanges().subscribe({
      next: (data) => {
        this.pendingEmail = data.pending_email;
        this.pendingPhone = data.pending_phone;
        if (this.pendingPhone) this.showPhoneOtpForm = true;
      }
    });
  }

  loadBookingStats() {
    this.bookingService.getMyBookings().subscribe({
      next: (data) => {

        const bookings = data || [];

        const today = new Date().toISOString().split('T')[0];

        this.upcomingBooking = bookings
          .filter(booking =>
            booking.status === 'pending' ||
            booking.status === 'confirmed'
          )
          .filter(booking => booking.event_date >= today)
          .sort((a, b) =>
            a.event_date.localeCompare(b.event_date)
          )[0] || null;

        // console.log('Today:', today);
        // console.log('Upcoming:', this.upcomingBooking);

        // console.log('Upcoming Booking:', this.upcomingBooking);
        // console.log("bookins", bookings)

        this.bookingStats = {
          totalBookings: bookings.length,

          pendingBookings: bookings.filter(
            booking => booking.status === 'pending'
          ).length,

          confirmedBookings: bookings.filter(
            booking => booking.status === 'confirmed'
          ).length,

          completedBookings: bookings.filter(
            booking => booking.status === 'completed'
          ).length,

          cancelledBookings: bookings.filter(
            booking => booking.status === 'cancelled'
          ).length,

          totalAmount: bookings.reduce(
            (total, booking) =>
              total + Number(booking.total_amount || 0),
            0
          )
        };

        console.log('Booking Stats:', this.bookingStats);
      },

      error: (error) => {
        console.error('Failed to load booking stats:', error);
      }
    });
  }

  loadWishList() {
    this.wishlistService.getMyWishlist().subscribe({
      next: (data) => {
        this.wishList = data || [];
        console.log("Wishlist", this.wishList);
      },
      error: (error) => {
        console.error("Wishlist error:", error);
        this.wishList = [];
      }
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

  // ── EMAIL CHANGE ──

  submitEmailChange() {
    if (this.emailForm.invalid) {
      this.emailForm.markAllAsTouched();
      return;
    }

    this.emailSubmitting = true;
    this.errorMessage = '';
    this.successMessage = '';

    const { new_email, current_password } = this.emailForm.value;

    this.accountService.requestEmailChange(new_email, current_password).subscribe({
      next: (res) => {
        this.emailSubmitting = false;
        this.successMessage = res.message;
        this.showEmailForm = false;
        this.emailForm.reset();
        this.loadPendingChanges();
      },
      error: (err) => {
        this.emailSubmitting = false;
        this.errorMessage = err.error?.detail || 'Failed to request email change';
      }
    });
  }

  cancelEmailChange() {
    this.accountService.cancelEmailChange().subscribe({
      next: () => {
        this.pendingEmail = null;
        this.successMessage = 'Pending email change cancelled';
      }
    });
  }

  // ── PHONE CHANGE ──

  submitPhoneChange() {
    if (this.phoneForm.invalid) {
      this.phoneForm.markAllAsTouched();
      return;
    }

    this.phoneSubmitting = true;
    this.errorMessage = '';
    this.successMessage = '';

    const { new_phone, current_password } = this.phoneForm.value;

    this.accountService.requestPhoneChange(new_phone, current_password).subscribe({
      next: (res) => {
        this.phoneSubmitting = false;
        this.successMessage = res.message;
        this.showPhoneForm = false;
        this.showPhoneOtpForm = true;
        this.phoneForm.reset();
        this.loadPendingChanges();
      },
      error: (err) => {
        this.phoneSubmitting = false;
        this.errorMessage = err.error?.detail || 'Failed to request phone change';
      }
    });
  }

  submitPhoneOtp() {
    if (this.phoneOtpForm.invalid) {
      this.phoneOtpForm.markAllAsTouched();
      return;
    }

    this.otpSubmitting = true;
    this.errorMessage = '';

    this.accountService.verifyPhoneChange(this.phoneOtpForm.value.otp_code).subscribe({
      next: (res) => {
        this.otpSubmitting = false;
        this.successMessage = res.message;
        this.showPhoneOtpForm = false;
        this.pendingPhone = null;
        this.phoneOtpForm.reset();
        // Refresh the displayed phone number
        this.authService.getMe().subscribe({ next: (data) => this.user = data });
      },
      error: (err) => {
        this.otpSubmitting = false;
        this.errorMessage = err.error?.detail || 'Invalid OTP';
      }
    });
  }

  resendPhoneOtp() {
    this.accountService.resendPhoneChangeOtp().subscribe({
      next: (res) => this.successMessage = res.message,
      error: (err) => this.errorMessage = err.error?.detail || 'Failed to resend OTP'
    });
  }

  cancelPhoneChange() {
    this.accountService.cancelPhoneChange().subscribe({
      next: () => {
        this.pendingPhone = null;
        this.showPhoneOtpForm = false;
        this.successMessage = 'Pending phone change cancelled';
      }
    });
  }
}