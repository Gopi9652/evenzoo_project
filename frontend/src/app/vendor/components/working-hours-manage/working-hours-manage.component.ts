import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { VendorService } from '../../../core/services/vendor.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';

interface DayRow {
  day_of_week: number;
  label: string;
  open_time: string;
  close_time: string;
  is_off_day: boolean;
  saving: boolean;
}

@Component({
  selector: 'app-working-hours-manage',
  standalone: true,
  imports: [CommonModule, FormsModule, MatButtonModule, MatSlideToggleModule, MatProgressSpinnerModule, NavbarComponent],
  templateUrl: './working-hours-manage.component.html',
  styleUrl: './working-hours-manage.component.scss'
})
export class WorkingHoursManageComponent implements OnInit {
  days: DayRow[] = [
    { day_of_week: 0, label: 'Monday',    open_time: '09:00', close_time: '18:00', is_off_day: false, saving: false },
    { day_of_week: 1, label: 'Tuesday',   open_time: '09:00', close_time: '18:00', is_off_day: false, saving: false },
    { day_of_week: 2, label: 'Wednesday', open_time: '09:00', close_time: '18:00', is_off_day: false, saving: false },
    { day_of_week: 3, label: 'Thursday',  open_time: '09:00', close_time: '18:00', is_off_day: false, saving: false },
    { day_of_week: 4, label: 'Friday',    open_time: '09:00', close_time: '18:00', is_off_day: false, saving: false },
    { day_of_week: 5, label: 'Saturday',  open_time: '09:00', close_time: '18:00', is_off_day: false, saving: false },
    { day_of_week: 6, label: 'Sunday',    open_time: '09:00', close_time: '18:00', is_off_day: true,  saving: false },
  ];
  loading = true;

  constructor(private vendorService: VendorService) {}

  ngOnInit() {
    this.loadHours();
  }

  loadHours() {
    this.loading = true;
    this.vendorService.getWorkingHours().subscribe({
      next: (data) => {
        // Merge saved hours into our default 7-day template so every day always renders,
        // even if the vendor has never set some days yet
        for (const saved of data) {
          const row = this.days.find(d => d.day_of_week === saved.day_of_week);
          if (row) {
            row.open_time = saved.open_time?.slice(0, 5) || row.open_time;
            row.close_time = saved.close_time?.slice(0, 5) || row.close_time;
            row.is_off_day = saved.is_off_day;
          }
        }
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  saveDay(day: DayRow) {
    day.saving = true;
    this.vendorService.setWorkingHours({
      day_of_week: day.day_of_week,
      open_time: day.is_off_day ? undefined : day.open_time,
      close_time: day.is_off_day ? undefined : day.close_time,
      is_off_day: day.is_off_day
    }).subscribe({
      next: () => {
        day.saving = false;
      },
      error: (err) => {
        day.saving = false;
        alert(err.error?.detail || `Failed to save ${day.label}`);
      }
    });
  }

  saveAll() {
    this.days.forEach(day => this.saveDay(day));
  }
}