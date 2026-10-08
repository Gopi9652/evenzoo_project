import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, ReactiveFormsModule, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonModule } from '@angular/material/button';
import { QuoteService } from '../../../core/services/quote.service';

@Component({
  selector: 'app-send-quote-dialog',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatCheckboxModule, MatButtonModule],
  templateUrl: './send-quote-dialog.component.html',
  styleUrl: './send-quote-dialog.component.scss'
})
export class SendQuoteDialogComponent implements OnInit {
  form: FormGroup;
  submitting = false;
  errorMessage = '';
  categoryOptions: { id: number; name: string }[] = [];

  constructor(
    private fb: FormBuilder,
    private quoteService: QuoteService,
    public dialogRef: MatDialogRef<SendQuoteDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: {
      eventPostId: number;
      customerName: string;
      items?: { category_id: number; category_name: string }[];
      singleCategoryId?: number;
      singleCategoryName?: string;
    }
  ) {
    this.form = this.fb.group({
      lines: this.fb.array([]),
      message: ['']
    });
  }

  get lines(): FormArray {
    return this.form.get('lines') as FormArray;
  }

  ngOnInit() {
    if (this.data.items && this.data.items.length > 0) {
      this.categoryOptions = this.data.items.map(i => ({ id: i.category_id, name: i.category_name }));
    } else if (this.data.singleCategoryId) {
      this.categoryOptions = [{ id: this.data.singleCategoryId, name: this.data.singleCategoryName || 'Service' }];
    }

    this.categoryOptions.forEach((opt, idx) => {
      this.lines.push(this.fb.group({
        category_id: [opt.id],
        category_name: [opt.name],
        selected: [idx === 0],   // first one pre-checked for convenience, rest optional
        quoted_amount: ['']
      }));
    });
  }

  get selectedCount(): number {
    return this.lines.controls.filter(c => c.value.selected).length;
  }

  submit() {
    const selectedLines = this.lines.controls
      .map(c => c.value)
      .filter(l => l.selected);

    if (selectedLines.length === 0) {
      this.errorMessage = 'Select at least one category to quote';
      return;
    }

    for (const line of selectedLines) {
      if (!line.quoted_amount || Number(line.quoted_amount) <= 0) {
        this.errorMessage = `Enter a price for ${line.category_name}`;
        return;
      }
    }

    this.submitting = true;
    this.errorMessage = '';

    if (selectedLines.length === 1) {
      // Single category — use the simpler endpoint
      this.quoteService.offerQuoteDirect(
        this.data.eventPostId,
        selectedLines[0].category_id,
        selectedLines[0].quoted_amount,
        this.form.value.message
      ).subscribe({
        next: () => { this.submitting = false; this.dialogRef.close('success'); },
        error: (err) => { this.submitting = false; this.errorMessage = err.error?.detail || 'Failed to send quote'; }
      });
    } else {
      // Multiple categories at once — bundle endpoint
      this.quoteService.offerBundleQuote(
        this.data.eventPostId,
        selectedLines.map(l => ({ category_id: l.category_id, quoted_amount: l.quoted_amount })),
        this.form.value.message
      ).subscribe({
        next: () => { this.submitting = false; this.dialogRef.close('success'); },
        error: (err) => { this.submitting = false; this.errorMessage = err.error?.detail || 'Failed to send quotes'; }
      });
    }
  }

  cancel() { this.dialogRef.close(); }
}