import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { VendorService } from '../../../core/services/vendor.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { VendorService as VendorServiceModel } from '../../../core/models/vendor.model';
import { ApprovalBannerComponent } from '../../../shared/components/approval-banner/approval-banner.component';

@Component({
  selector: 'app-services-manage',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatFormFieldModule,
    MatInputModule, MatSelectModule, MatButtonModule,
    MatIconModule, MatProgressSpinnerModule, NavbarComponent,ApprovalBannerComponent
  ],
  templateUrl: './services-manage.component.html',
  styleUrl: './services-manage.component.scss'
})
export class ServicesManageComponent implements OnInit {
  services: VendorServiceModel[] = [];
  serviceForm: FormGroup;
  loading = true;
  submitting = false;
  showForm = false;

  constructor(
    private fb: FormBuilder,
    private vendorService: VendorService
  ) {
    this.serviceForm = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      price: ['', [Validators.required, Validators.min(1)]],
      price_type: ['fixed', Validators.required]
    });
  }

  ngOnInit() {
    this.loadServices();
  }

  loadServices() {
    this.loading = true;
    this.vendorService.getMyProfile().subscribe({
      next: (profile) => {
        this.vendorService.getVendorServices(profile.id).subscribe({
          next: (data) => {
            this.services = data;
            this.loading = false;
          },
          error: () => this.loading = false
        });
      },
      error: () => this.loading = false
    });
  }

  toggleForm() {
    this.showForm = !this.showForm;
    this.serviceForm.reset({ price_type: 'fixed' });
  }

  onSubmit() {
    if (this.serviceForm.invalid) {
      this.serviceForm.markAllAsTouched();
      return;
    }

    this.submitting = true;
    this.vendorService.addService(this.serviceForm.value).subscribe({
      next: () => {
        this.submitting = false;
        this.showForm = false;
        this.serviceForm.reset({ price_type: 'fixed' });
        this.loadServices();
      },
      error: (err) => {
        this.submitting = false;
        alert(err.error?.detail || 'Failed to add service');
      }
    });
  }

  deleteService(serviceId: number) {
    if (!confirm('Delete this service? This cannot be undone.')) return;

    this.vendorService.deleteService(serviceId).subscribe({
      next: () => this.loadServices(),
      error: (err) => alert(err.error?.detail || 'Failed to delete service')
    });
  }
}