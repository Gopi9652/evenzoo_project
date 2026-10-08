import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { QuoteService } from '../../../core/services/quote.service';

export interface RespondQuoteDialogData {
  quoteId: number;
  customerName?: string;
  categoryName?: string;   // may be undefined if the customer didn't pick one — "General enquiry"
  eventTitle?: string;
  existingMessage?: string;
}

@Component({
  selector: 'app-respond-quote-dialog',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatButtonModule],
  templateUrl: './respond-quote-dialog.component.html',
  styleUrl: './respond-quote-dialog.component.scss'
})
export class RespondQuoteDialogComponent {
  form: FormGroup;
  submitting = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private quoteService: QuoteService,
    public dialogRef: MatDialogRef<RespondQuoteDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: RespondQuoteDialogData
  ) {
    this.form = this.fb.group({
      quoted_amount: ['', [Validators.required, Validators.min(1)]],
      message: ['']
    });
  }

  submit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.submitting = true;
    this.errorMessage = '';

    this.quoteService.respondToQuote(
      this.data.quoteId,
      this.form.value.quoted_amount,
      this.form.value.message
    ).subscribe({
      next: () => {
        this.submitting = false;
        this.dialogRef.close('success');
      },
      error: (err) => {
        this.submitting = false;
        this.errorMessage = err.error?.detail || 'Failed to send quote';
      }
    });
  }

  cancel() {
    this.dialogRef.close();
  }
}