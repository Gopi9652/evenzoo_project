import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-otp-verify',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule,
    MatFormFieldModule, MatInputModule, MatButtonModule,
    MatCardModule, MatProgressSpinnerModule
  ],
  templateUrl: './otp-verify.component.html',
  styleUrl: './otp-verify.component.scss'
})
export class OtpVerifyComponent implements OnInit {
  otpForm: FormGroup;
  loading = false;
  errorMessage = '';
  successMessage = '';
  phone = '';
  purpose = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.otpForm = this.fb.group({
      otp_code: ['', [Validators.required, Validators.pattern(/^\d{6}$/)]]
    });
  }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.phone = params['phone'];
      this.purpose = params['purpose'];
    });
  }

  onSubmit() {
    if (this.otpForm.invalid) {
      this.otpForm.markAllAsTouched();
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.authService.verifyOtp(
      this.phone,
      this.otpForm.value.otp_code,
      this.purpose
    ).subscribe({
      next: () => {
        this.loading = false;
        this.successMessage = 'Phone verified successfully! Redirecting to login...';
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err.error?.detail || 'OTP verification failed.';
      }
    });
  }

  resendOtp() {
    this.authService.sendOtp(this.phone, this.purpose).subscribe({
      next: () => {
        this.errorMessage = '';
        this.successMessage = 'OTP resent successfully!';
        setTimeout(() => this.successMessage = '', 3000);
      }
    });
  }
}