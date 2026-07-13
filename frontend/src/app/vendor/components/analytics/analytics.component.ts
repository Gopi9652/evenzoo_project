import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData } from 'chart.js';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { VendorService } from '../../../core/services/vendor.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [
    CommonModule,
    BaseChartDirective,
    MatProgressSpinnerModule,
    NavbarComponent
  ],
  templateUrl: './analytics.component.html',
  styleUrl: './analytics.component.scss'
})
export class AnalyticsComponent implements OnInit {

  analytics: any = null;
  loading = true;

  bookingsChartData: ChartData<'line'> = {
    labels: [],
    datasets: []
  };

  revenueChartData: ChartData<'bar'> = {
    labels: [],
    datasets: []
  };

  statusChartData: ChartData<'doughnut'> = {
    labels: [],
    datasets: []
  };

  ratingChartData: ChartData<'bar'> = {
    labels: [],
    datasets: []
  };

  lineOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: false
  };

  barOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: true,
    maintainAspectRatio: false
  };

  doughnutOptions: ChartConfiguration<'doughnut'>['options'] = {
    responsive: true,
    maintainAspectRatio: false
  };

  monthNames = [
    'Jan','Feb','Mar','Apr','May','Jun',
    'Jul','Aug','Sep','Oct','Nov','Dec'
  ];

  constructor(private vendorService: VendorService) {}

  ngOnInit(): void {
    this.vendorService.getMyAnalytics().subscribe({
      next: (data) => {
        this.analytics = data;
        this.buildCharts(data);
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  buildCharts(data: any): void {

    this.bookingsChartData = {
      labels: data.monthly_bookings.map((m: any) => this.monthNames[m.month - 1]),
      datasets: [
        {
          label: 'Bookings',
          data: data.monthly_bookings.map((m: any) => m.count),
          borderColor: '#e8650a',
          backgroundColor: 'rgba(232,101,10,0.1)',
          tension: 0.3,
          fill: true
        }
      ]
    };

    this.revenueChartData = {
      labels: data.monthly_revenue.map((m: any) => this.monthNames[m.month - 1]),
      datasets: [
        {
          label: 'Revenue (₹)',
          data: data.monthly_revenue.map((m: any) => m.revenue),
          backgroundColor: '#16a34a'
        }
      ]
    };

    const statusColors: Record<string, string> = {
      pending: '#f5a623',
      confirmed: '#e8650a',
      completed: '#16a34a',
      cancelled: '#dc2626'
    };

    const statusLabels = Object.keys(data.status_breakdown);

    this.statusChartData = {
      labels: statusLabels.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
      datasets: [
        {
          data: statusLabels.map(s => data.status_breakdown[s]),
          backgroundColor: statusLabels.map(s => statusColors[s] || '#94a3b8')
        }
      ]
    };

    const ratingLabels = ['1★', '2★', '3★', '4★', '5★'];

    this.ratingChartData = {
      labels: ratingLabels,
      datasets: [
        {
          label: 'Reviews',
          data: [1,2,3,4,5].map(r => data.rating_distribution[r] || 0),
          backgroundColor: '#f5a623'
        }
      ]
    };
  }
}