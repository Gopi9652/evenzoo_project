import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AdminService } from '../../../core/services/admin.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';

@Component({
  selector: 'app-admin-booking-detail',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule, NavbarComponent],
  templateUrl: './booking-detail.component.html',
  styleUrl: './booking-detail.component.scss'
})
export class AdminBookingDetailComponent implements OnInit {
  data: any = null;
  loading = true;

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private adminService: AdminService
  ) {}

  ngOnInit() {
    const bookingId = Number(this.route.snapshot.paramMap.get('id'));
    this.adminService.getBookingDetail(bookingId).subscribe({
      next: (data) => {
        this.data = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  statusColor(status: string): string {
    const colors: Record<string, string> = {
      pending: '#f5a623', confirmed: '#e8650a', completed: '#16a34a', cancelled: '#dc2626'
    };
    return colors[status] || '#64748b';
  }
}