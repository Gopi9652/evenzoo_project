import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { QuoteService } from '../../../core/services/quote.service';
import { VendorService } from '../../../core/services/vendor.service';
import { Category } from '../../../core/models/vendor.model';

@Component({
  selector: 'app-request-quote-dialog',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatSelectModule, MatButtonModule],
  templateUrl: './request-quote-dialog.component.html',
  styleUrl: './request-quote-dialog.component.scss'
})
export class RequestQuoteDialogComponent implements OnInit {
  form: FormGroup;
  submitting = false;
  errorMessage = '';
  categories: Category[] = [];

  constructor(
    private fb: FormBuilder,
    private quoteService: QuoteService,
    private vendorService: VendorService,
    public dialogRef: MatDialogRef<RequestQuoteDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { vendorId: number; vendorName: string; eventPostId?: number; categoryId?: number }
  ) {
    this.form = this.fb.group({
      category_id: [data.categoryId || null],
      target_budget: [''],
      message: ['']
    });
  }

  ngOnInit() {
    this.vendorService.getCategories().subscribe({ next: (data) => this.categories = data });
  }

  submit() {
    this.submitting = true;
    this.errorMessage = '';

    // target_budget is folded into the message as context for the vendor —
    // it's not a formal field on the Quote model, just a helpful note
    let fullMessage = this.form.value.message || '';
    if (this.form.value.target_budget) {
      fullMessage = `My target budget is around ₹${this.form.value.target_budget}. ${fullMessage}`.trim();
    }

    this.quoteService.requestQuote(
      this.data.vendorId,
      this.data.eventPostId,
      this.form.value.category_id,
      fullMessage || undefined
    ).subscribe({
      next: () => {
        this.submitting = false;
        this.dialogRef.close('success');
      },
      error: (err) => {
        this.submitting = false;
        this.errorMessage = err.error?.detail || 'Failed to request quote';
      }
    });
  }

  cancel() { this.dialogRef.close(); }
}