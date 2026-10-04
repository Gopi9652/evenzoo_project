import { Routes } from '@angular/router';

export const customerRoutes: Routes = [
    {
        path: 'home',
        loadComponent: () =>
            import('./components/home/home.component').then((m) => m.HomeComponent),
    },
    {
        path: 'vendor/:id',
        loadComponent: () =>
            import('./components/vendor-detail/vendor-detail.component').then((m) => m.VendorDetailComponent),
    },
    {
        path: 'bookings',
        loadComponent: () =>
            import('./components/my-bookings/my-bookings.component').then((m) => m.MyBookingsComponent),
    },
    {
        path: 'booking/:id',
        loadComponent: () =>
            import('./components/booking-detail/booking-detail.component').then((m) => m.BookingDetailComponent),
    },
    {
        path: 'wishlist',
        loadComponent: () => 
            import('./components/my-wishlist/my-wishlist.component').then((m) => m.MyWishlistComponent),
    },
    {
        path: 'reviews',
        loadComponent: () =>
            import('./components/my-reviews/my-reviews.component').then((m) => m.MyReviewsComponent),
    },
    {
        path: 'post/create',
        loadComponent: () =>
            import('./components/create-event-post/create-event-post.component').then((m) => m.CreateEventPostComponent),
    },
    {
        path: 'my-posts',
        loadComponent: () =>
            import('./components/my-event-posts/my-event-posts.component').then((m) => m.MyEventPostsComponent),
    },
    {
        path: 'compare',
        loadComponent: () => 
            import('./components/vendor-compare/vendor-compare.component').then((m) => m.VendorCompareComponent),
    },
    {
        path: 'vendor-card',
        loadComponent: () =>
            import('./components/vendor-card/vendor-card.component').then((m) => m.VendorCardComponent)
    }
]