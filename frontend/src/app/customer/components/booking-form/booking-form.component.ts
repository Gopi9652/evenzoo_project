import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonModule } from '@angular/material/button';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BookingService, EventType } from '../../../core/services/booking.service';

@Component({
  selector: 'app-booking-form',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatDialogModule,
    MatFormFieldModule, MatInputModule, MatSelectModule,
    MatCheckboxModule, MatButtonModule, MatDatepickerModule,
    MatNativeDateModule, MatProgressSpinnerModule
  ],
  templateUrl: './booking-form.component.html',
  styleUrl: './booking-form.component.scss'
})
export class BookingFormComponent implements OnInit {
  bookingForm: FormGroup;
  eventTypes: EventType[] = [];
  loading = false;
  submitting = false;
  errorMessage = '';
  minDate = new Date();
  isOtherSelected = false;   // ← NEW

  readonly OTHER_VALUE = '__other__';   // sentinel value for the dropdown

  constructor(
    private fb: FormBuilder,
    private bookingService: BookingService,
    public dialogRef: MatDialogRef<BookingFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.bookingForm = this.fb.group({
      event_type_id: ['', Validators.required],
      custom_event_type: [''],   // ← NEW, no validator yet — conditional below
      event_date: ['', Validators.required],
      event_time: [''],
      event_location: ['', Validators.required],
      guests_count: [''],
      special_requests: [''],
      service_ids: [[]]
    });
  }

  ngOnInit() {
    this.bookingService.getEventTypes().subscribe({
      next: (data) => this.eventTypes = data
    });

    // React to event type changes
    this.bookingForm.get('event_type_id')?.valueChanges.subscribe(value => {
      this.isOtherSelected = value === this.OTHER_VALUE;
      const customControl = this.bookingForm.get('custom_event_type');
      if (this.isOtherSelected) {
        customControl?.setValidators([Validators.required, Validators.minLength(3)]);
      } else {
        customControl?.clearValidators();
        customControl?.setValue('');
      }
      customControl?.updateValueAndValidity();
    });
  }

  toggleService(serviceId: number, checked: boolean) {
    const current = this.bookingForm.value.service_ids || [];
    if (checked) {
      this.bookingForm.patchValue({ service_ids: [...current, serviceId] });
    } else {
      this.bookingForm.patchValue({
        service_ids: current.filter((id: number) => id !== serviceId)
      });
    }
  }

  isServiceSelected(serviceId: number): boolean {
    return (this.bookingForm.value.service_ids || []).includes(serviceId);
  }

  get totalAmount(): number {
    const selectedIds = this.bookingForm.value.service_ids || [];
    return this.data.services
      .filter((s: any) => selectedIds.includes(s.id))
      .reduce((sum: number, s: any) => sum + Number(s.price), 0);
  }

  onSubmit() {
    if (this.bookingForm.invalid) {
      this.bookingForm.markAllAsTouched();
      return;
    }

    if ((this.bookingForm.value.service_ids || []).length === 0) {
      this.errorMessage = 'Please select at least one service';
      return;
    }

    this.submitting = true;
    this.errorMessage = '';

    const formValue = this.bookingForm.value;
    const eventDate = formValue.event_date instanceof Date
      ? formValue.event_date.toISOString().split('T')[0]
      : formValue.event_date;

    const payload: any = {
      vendor_id: this.data.vendorId,
      event_date: eventDate,
      event_time: formValue.event_time || undefined,
      custom_event_type : formValue.custom_event_type || '',
      event_location: formValue.event_location,
      guests_count: formValue.guests_count || undefined,
      special_requests: formValue.special_requests || undefined,
      service_ids: formValue.service_ids
    };

    // Send either a real event_type_id OR a custom_event_type — never both
    if (this.isOtherSelected) {
      payload.custom_event_type = formValue.custom_event_type;
    } else {
      payload.event_type_id = formValue.event_type_id;
    }

    this.bookingService.createBooking(payload).subscribe({
      next: () => {
        this.submitting = false;
        this.dialogRef.close('success');
      },
      error: (err) => {
        this.submitting = false;
        this.errorMessage = err.error?.detail || 'Failed to create booking';
      }
    });
  }

  onCancel() {
    this.dialogRef.close();
  }
}