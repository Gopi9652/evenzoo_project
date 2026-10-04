import { Routes } from '@angular/router';

export const vendorRoutes: Routes = [
    {
        path: 'dashboard',
        loadComponent: () =>
            import('./components/dashboard/dashboard.component').then((m) => m.DashboardComponent),
    },
    {
        path: 'profile',
        loadComponent: () => 
            import('./components/profile-edit/profile-edit.component').then((m) => m.ProfileEditComponent),
    },
    {
        path: 'services',
        loadComponent: () =>
            import('./components/services-manage/services-manage.component').then((m) => m.ServicesManageComponent),
    },
    {
        path: 'bookings',
        loadComponent: () =>
            import('./components/bookings-manage/bookings-manage.component').then((m) => m.BookingsManageComponent),
    },
    {
        path: 'reviews',
        loadComponent: () =>
            import('./components/reviews-view/reviews-view.component').then((m) => m.ReviewsViewComponent),
    },
    {
        path: 'documents',
        loadComponent: () =>
            import ('./components/documents-manage/documents-manage.component').then((m) => m.DocumentsManageComponent),
    },
    {
        path: 'analytics',
        loadComponent: () =>
            import('./components/analytics/analytics.component').then((m) => m.AnalyticsComponent),
    },
    {
        path: 'event-posts',
        loadComponent: () =>
            import('./components/event-posts-feed/event-posts-feed.component').then((m) => m.EventPostsFeedComponent),
    },
    {
        path: 'availability',
        loadComponent: () =>
            import('./components/availability-manage/availability-manage.component').then((m) => m.AvailabilityManageComponent),
    },
    {
        path: 'working-hours',
        loadComponent: () =>
            import('./components/working-hours-manage/working-hours-manage.component').then((m) => m.WorkingHoursManageComponent),
    },
    {
    path: 'photos',
    loadComponent: () =>
      import('./components/photos-manage/photos-manage.component').then((m) => m.PhotosManageComponent),
  },
]