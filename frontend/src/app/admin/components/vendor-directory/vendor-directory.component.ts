import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AdminService } from '../../../core/services/admin.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-vendor-directory',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatButtonToggleModule, MatProgressSpinnerModule, NavbarComponent, FormsModule],
  templateUrl: './vendor-directory.component.html',
  styleUrl: './vendor-directory.component.scss'
})
export class VendorDirectoryComponent implements OnInit {
  vendors: any[] = [];
  loading = true;
  viewMode: 'grid' | 'list' = 'grid';

  constructor(private adminService: AdminService) {}

  ngOnInit() {
    this.adminService.getAllVendors().subscribe({
      next: (data) => {
        this.vendors = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }
}