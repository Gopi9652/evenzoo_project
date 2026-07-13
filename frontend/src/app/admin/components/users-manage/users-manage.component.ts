import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AdminService } from '../../../core/services/admin.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';

@Component({
  selector: 'app-users-manage',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatSelectModule, MatButtonModule,
    MatIconModule, MatProgressSpinnerModule, NavbarComponent
  ],
  templateUrl: './users-manage.component.html',
  styleUrl: './users-manage.component.scss'
})
export class UsersManageComponent implements OnInit {
  users: any[] = [];
  loading = true;
  roleFilter = '';

  constructor(private adminService: AdminService) {}

  ngOnInit() {
    this.loadUsers();
  }

  loadUsers() {
    this.loading = true;
    this.adminService.getAllUsers(this.roleFilter || undefined).subscribe({
      next: (data) => {
        this.users = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  toggleStatus(user: any) {
    const newStatus = !user.is_active;
    const action = newStatus ? 'reactivate' : 'suspend';

    if (!confirm(`Are you sure you want to ${action} ${user.name}?`)) return;

    this.adminService.toggleUserStatus(user.id, newStatus).subscribe({
      next: () => {
        user.is_active = newStatus;
      },
      error: (err) => alert(err.error?.detail || `Failed to ${action} user`)
    });
  }
}