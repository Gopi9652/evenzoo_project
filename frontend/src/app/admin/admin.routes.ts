import { Routes } from "@angular/router";

export const adminRoutes: Routes = [
    {
        path: 'dashboard',
        loadComponent: () =>
            import('./components/dashboard/dashboard.component').then((m) => m.DashboardComponent),
    },
    {
        path: 'vendors',
        loadComponent: () =>
            import('./components/vendor-approvals/vendor-approvals.component').then((m) => m.VendorApprovalsComponent),
    },
    {
        path: 'bookings',
        loadComponent: () =>
            import('./components/bookings-overview/bookings-overview.component').then((m) => m.BookingsOverviewComponent),
    },
    {
        path: 'users',
        loadComponent: () =>
            import('./components/users-manage/users-manage.component').then((m) => m.UsersManageComponent),
    },
    {
        path: 'bookings/:id',
        loadComponent: () =>
            import('./components/booking-detail/booking-detail.component').then((m) => m.AdminBookingDetailComponent),
    },
    {
        path: 'directory',
        loadComponent: () =>
          import('./components/vendor-directory/vendor-directory.component').then(m => m.VendorDirectoryComponent),
    },
    {
    path: 'deletion-requests',
    loadComponent: () =>
      import('./components/deletion-requests/deletion-requests.component').then(m => m.DeletionRequestsComponent),
  }
]