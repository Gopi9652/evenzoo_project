import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { VendorService } from '../../../core/services/vendor.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-documents-manage',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatButtonModule, MatSelectModule,
    MatIconModule, MatProgressSpinnerModule, NavbarComponent
  ],
  templateUrl: './documents-manage.component.html',
  styleUrl: './documents-manage.component.scss'
})
export class DocumentsManageComponent implements OnInit {
  documents: any[] = [];
  loading = true;
  uploading = false;
  selectedType = 'aadhar';

  documentTypes = [
    { value: 'aadhar', label: 'Aadhar Card' },
    { value: 'pan', label: 'PAN Card' },
    { value: 'gst', label: 'GST Certificate' },
    { value: 'license', label: 'Business License' }
  ];

  constructor(
    private vendorService: VendorService,
    private http: HttpClient
  ) {}

  ngOnInit() {
    this.loadDocuments();
  }

  loadDocuments() {
    this.loading = true;
    this.vendorService.getMyDocuments().subscribe({
      next: (data) => {
        this.documents = data;
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

    this.http.post(
      `${environment.apiUrl}/vendors/me/upload-document?document_type=${this.selectedType}`,
      formData
    ).subscribe({
      next: () => {
        this.uploading = false;
        this.loadDocuments();
      },
      error: (err) => {
        this.uploading = false;
        alert('Upload failed: ' + (err.error?.detail || 'Unknown error'));
      }
    });

    event.target.value = '';
  }

  deleteDocument(docId: number) {
    if (!confirm('Delete this document?')) return;

    this.vendorService.deleteDocument(docId).subscribe({
      next: () => this.loadDocuments(),
      error: (err) => alert(err.error?.detail || 'Failed to delete document')
    });
  }

  typeLabel(type: string): string {
    return this.documentTypes.find(t => t.value === type)?.label || type;
  }
}