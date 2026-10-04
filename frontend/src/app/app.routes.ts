import { Routes } from '@angular/router';
// import { LoginComponent } from './core/components/login/login.component';
// import { RegisterComponent } from './core/components/register/register.component';
// import { OtpVerifyComponent } from './core/components/otp-verify/otp-verify.component';
// import { HomeComponent } from './customer/components/home/home.component';
// import { VendorDetailComponent } from './customer/components/vendor-detail/vendor-detail.component';
// import { MyBookingsComponent } from './customer/components/my-bookings/my-bookings.component';
// import { BookingDetailComponent } from './customer/components/booking-detail/booking-detail.component';
// import { DashboardComponent as VendorDashboardComponent } from './vendor/components/dashboard/dashboard.component';
// import { ProfileEditComponent } from './vendor/components/profile-edit/profile-edit.component';
// import { ServicesManageComponent } from './vendor/components/services-manage/services-manage.component';
// import { BookingsManageComponent } from './vendor/components/bookings-manage/bookings-manage.component';
// import { DashboardComponent as AdminDashboardComponent } from './admin/components/dashboard/dashboard.component';
// import { VendorApprovalsComponent } from './admin/components/vendor-approvals/vendor-approvals.component';
// import { BookingsOverviewComponent } from './admin/components/bookings-overview/bookings-overview.component';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';
// import { PhotosManageComponent } from './vendor/components/photos-manage/photos-manage.component';

// import { ForgotPasswordComponent } from './core/components/forgot-password/forgot-password.component';
// import { ResetPasswordComponent } from './core/components/reset-password/reset-password.component';
// import { MyWishlistComponent } from './customer/components/my-wishlist/my-wishlist.component';

// import { ChangePasswordComponent } from './core/components/change-password/change-password.component';
// import { ReviewsViewComponent } from './vendor/components/reviews-view/reviews-view.component';
import { SplashComponent } from './core/components/splash/splash.component';


// import { MyReviewsComponent } from './customer/components/my-reviews/my-reviews.component';
// import { UsersManageComponent } from './admin/components/users-manage/users-manage.component';

// import { DocumentsManageComponent } from './vendor/components/documents-manage/documents-manage.component';

// import { MyProfileComponent } from './shared/components/my-profile/my-profile.component';
// import { VendorDirectoryComponent } from './admin/components/vendor-directory/vendor-directory.component';
// import { SessionsManageComponent } from './shared/components/sessions-manage/sessions-manage.component';

// import { ConversationsListComponent } from './shared/components/conversations-list/conversations-list.component';
// import { ChatWindowComponent } from './shared/components/chat-window/chat-window.component';

// import { AnalyticsComponent } from './vendor/components/analytics/analytics.component';


// import { PrivacyPolicyComponent } from './core/components/privacy-policy/privacy-policy.component';
// import { TermsOfServiceComponent } from './core/components/terms-of-service/terms-of-service.component';
// import { RefundPolicyComponent } from './core/components/refund-policy/refund-policy.component';
// import { CookiePolicyComponent } from './core/components/cookie-policy/cookie-policy.component';
// import { ContactComponent } from './core/components/contact/contact.component';
// import { CreateEventPostComponent } from './customer/components/create-event-post/create-event-post.component';
// import { MyEventPostsComponent } from './customer/components/my-event-posts/my-event-posts.component';
// import { EventPostsFeedComponent } from './vendor/components/event-posts-feed/event-posts-feed.component';

// import { AvailabilityManageComponent } from './vendor/components/availability-manage/availability-manage.component';
// import { WorkingHoursManageComponent } from './vendor/components/working-hours-manage/working-hours-manage.component';
// import { PrivacySettingsComponent } from './shared/components/privacy-settings/privacy-settings.component';
// import { DeletionRequestsComponent } from './admin/components/deletion-requests/deletion-requests.component';

// import { VendorCompareComponent } from './customer/components/vendor-compare/vendor-compare.component';

// import { AdminBookingDetailComponent } from './admin/components/booking-detail/booking-detail.component';
// import { ConfirmEmailComponent } from './core/components/confirm-email/confirm-email.component';


export const routes: Routes = [
  // { path: '', component: SplashComponent },
  // { path: 'login', component: LoginComponent },
  // { path: 'register', component: RegisterComponent },
  // { path: 'verify-otp', component: OtpVerifyComponent },
  // { path: 'vendor/photos', component: PhotosManageComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  // { path: 'forgot-password', component: ForgotPasswordComponent },
  // { path: 'reset-password', component: ResetPasswordComponent },
  // { path: 'settings/change-password', component: ChangePasswordComponent, canActivate: [authGuard] },
  // { path: 'sessions', component: SessionsManageComponent, canActivate: [authGuard] },
  // { path: 'profile', component: MyProfileComponent, canActivate: [authGuard] },
  // { path: 'admin/directory', component: VendorDirectoryComponent, canActivate: [authGuard, roleGuard(['admin'])] },
  // { path: 'messages', component: ConversationsListComponent, canActivate: [authGuard] },
  // { path: 'chat/booking/:bookingId', component: ChatWindowComponent, canActivate: [authGuard], runGuardsAndResolvers: 'always' },
  // { path: 'chat/user/:userId', component: ChatWindowComponent, canActivate: [authGuard], runGuardsAndResolvers: 'always' },
  // { path: 'privacy-policy', component: PrivacyPolicyComponent },
  // { path: 'terms-of-service', component: TermsOfServiceComponent },
  // { path: 'refund-policy', component: RefundPolicyComponent },
  // { path: 'cookie-policy', component: CookiePolicyComponent },
  // { path: 'contact', component: ContactComponent },
  // { path: 'settings/privacy', component: PrivacySettingsComponent, canActivate: [authGuard] },

  // { path: 'admin/deletion-requests', component: DeletionRequestsComponent, canActivate: [authGuard, roleGuard(['admin'])] },
  // { path: 'settings/confirm-email', component: ConfirmEmailComponent },

  // Customer routes
  // { path: 'customer/home', component: HomeComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  // { path: 'customer/vendor/:id', component: VendorDetailComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  // { path: 'customer/bookings', component: MyBookingsComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  // { path: 'customer/booking/:id', component: BookingDetailComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  // { path: 'customer/wishlist', component: MyWishlistComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  // { path: 'customer/reviews', component: MyReviewsComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  // { path: 'customer/post/create', component: CreateEventPostComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  // { path: 'customer/my-posts', component: MyEventPostsComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  // { path: 'customer/compare', component: VendorCompareComponent, canActivate: [authGuard, roleGuard(['customer'])] },

  // Vendor routes
  // { path: 'vendor/dashboard', component: VendorDashboardComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  // { path: 'vendor/profile', component: ProfileEditComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  // { path: 'vendor/services', component: ServicesManageComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  // { path: 'vendor/bookings', component: BookingsManageComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  // { path: 'vendor/reviews', component: ReviewsViewComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  // { path: 'vendor/documents', component: DocumentsManageComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  // { path: 'vendor/analytics', component: AnalyticsComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  // { path: 'vendor/event-posts', component: EventPostsFeedComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  // { path: 'vendor/availability', component: AvailabilityManageComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  // { path: 'vendor/working-hours', component: WorkingHoursManageComponent, canActivate: [authGuard, roleGuard(['vendor'])] },

  // Admin routes
  // { path: 'admin/dashboard', component: AdminDashboardComponent, canActivate: [authGuard, roleGuard(['admin'])] },
  // { path: 'admin/vendors', component: VendorApprovalsComponent, canActivate: [authGuard, roleGuard(['admin'])] },
  // { path: 'admin/bookings', component: BookingsOverviewComponent, canActivate: [authGuard, roleGuard(['admin'])] },
  // { path: 'admin/users', component: UsersManageComponent, canActivate: [authGuard, roleGuard(['admin'])] },
  // { path: 'admin/bookings/:id', component: AdminBookingDetailComponent, canActivate: [authGuard, roleGuard(['admin'])] },
  
  // Components are loaded using lazy loading
  { path: '', component: SplashComponent },
  {
    path: 'browse',
    loadComponent: () =>
      import('./customer/components/home/home.component').then((m) => m.HomeComponent),
  },
  {
    path: 'browse/vendor/:slug',
    loadComponent: () =>
      import('./customer/components/vendor-detail/vendor-detail.component').then((m) => m.VendorDetailComponent),
  },
  {
    path: 'browse/compare',
    loadComponent: () =>
      import('./customer/components/vendor-compare/vendor-compare.component').then((m) => m.VendorCompareComponent),
  },
  // Old paths kept working via redirect
  { path: 'customer/home', redirectTo: 'browse', pathMatch: 'full' },
  { path: 'customer/vendor/:id', redirectTo: 'browse/vendor/:id', pathMatch: 'full' },
  { path: 'customer/compare', redirectTo: 'browse/compare', pathMatch: 'full' },
  {
    path: "login",
    loadComponent: () => 
      import('./core/components/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'register',
    loadComponent: () => 
      import('./core/components/register/register.component').then((m) => m.RegisterComponent),
  },
  {
    path: 'verify-otp',
    loadComponent: () =>
      import('./core/components/otp-verify/otp-verify.component').then((m) => m.OtpVerifyComponent),
  },
  {
    path: 'forgot-password',
    loadComponent: () =>
      import('./core/components/forgot-password/forgot-password.component').then((m) => m.ForgotPasswordComponent),
  },
  {
    path: 'reset-password',
    loadComponent: () =>
      import('./core/components/reset-password/reset-password.component').then((m) => m.ResetPasswordComponent),
  },
  {
    path: 'settings/change-password',
    loadComponent: () =>
      import('./core/components/change-password/change-password.component').then((m) => m.ChangePasswordComponent),
    canActivate: [authGuard],
  },
  {
    path: 'sessions',
    loadComponent: () =>
      import('./shared/components/sessions-manage/sessions-manage.component').then(m => m.SessionsManageComponent),
    canActivate: [authGuard],
  },
  {
    path: 'profile',
    loadComponent: () =>
      import('./shared/components/my-profile/my-profile.component').then(m => m.MyProfileComponent),
    canActivate: [authGuard],
  },
  {
    path: 'messages',
    loadComponent: () =>
      import('./shared/components/conversations-list/conversations-list.component').then(m => m.ConversationsListComponent),
    canActivate: [authGuard],
  },
  {
    path: 'chat/booking/:bookingId',
    loadComponent: () =>
      import('./shared/components/chat-window/chat-window.component').then(m => m.ChatWindowComponent),
    canActivate: [authGuard],
    runGuardsAndResolvers: 'always',
  },
  {
    path: 'chat/user/:userId',
    loadComponent: () =>
      import('./shared/components/chat-window/chat-window.component').then(m => m.ChatWindowComponent),
    canActivate: [authGuard],
    runGuardsAndResolvers: 'always',
  },
  {
    path: 'privacy-policy',
    loadComponent: () =>
      import('./core/components/privacy-policy/privacy-policy.component').then(m => m.PrivacyPolicyComponent),
  },
  {
    path: 'terms-of-service',
    loadComponent: () =>
      import('./core/components/terms-of-service/terms-of-service.component').then(m => m.TermsOfServiceComponent),
  },
  {
    path: 'refund-policy',
    loadComponent: () =>
      import('./core/components/refund-policy/refund-policy.component').then(m => m.RefundPolicyComponent),
  },
  {
    path: 'cookie-policy',
    loadComponent: () =>
      import('./core/components/cookie-policy/cookie-policy.component').then(m => m.CookiePolicyComponent),
  },
  {
    path: 'contact',
    loadComponent: () =>
      import('./core/components/contact/contact.component').then(m => m.ContactComponent),
  },
  {
    path: 'settings/privacy',
    loadComponent: () =>
      import('./shared/components/privacy-settings/privacy-settings.component').then(m => m.PrivacySettingsComponent),
    canActivate: [authGuard],
  },
  {
    path: 'settings/confirm-email',
    loadComponent: () =>
      import('./core/components/confirm-email/confirm-email.component').then(m => m.ConfirmEmailComponent),
  },
  {
    path: 'customer',
    loadChildren: () =>
      import('./customer/customer.routes').then((m) => m.customerRoutes),
    canActivateChild: [authGuard, roleGuard(['customer'])],
  },
  {
    path: 'vendor',
    loadChildren: () =>
        import('./vendor/vendor.routes').then((m) => m.vendorRoutes),
    canActivateChild: [authGuard, roleGuard(['vendor'])],
  },
  {
    path: 'admin',
    loadChildren: () =>
      import('./admin/admin.routes').then((m) => m.adminRoutes),
    canActivateChild: [authGuard, roleGuard(['admin'])]
  },
  {
    path: 'help-support',
    loadComponent: () =>
      import('./shared/components/help-support/help-support.component').then((m) => m.HelpSupportComponent),
  }
];