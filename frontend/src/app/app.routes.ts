import { Routes } from '@angular/router';
import { LoginComponent } from './core/components/login/login.component';
import { RegisterComponent } from './core/components/register/register.component';
import { OtpVerifyComponent } from './core/components/otp-verify/otp-verify.component';
import { HomeComponent } from './customer/components/home/home.component';
import { VendorDetailComponent } from './customer/components/vendor-detail/vendor-detail.component';
import { MyBookingsComponent } from './customer/components/my-bookings/my-bookings.component';
import { BookingDetailComponent } from './customer/components/booking-detail/booking-detail.component';
import { DashboardComponent as VendorDashboardComponent } from './vendor/components/dashboard/dashboard.component';
import { ProfileEditComponent } from './vendor/components/profile-edit/profile-edit.component';
import { ServicesManageComponent } from './vendor/components/services-manage/services-manage.component';
import { BookingsManageComponent } from './vendor/components/bookings-manage/bookings-manage.component';
import { DashboardComponent as AdminDashboardComponent } from './admin/components/dashboard/dashboard.component';
import { VendorApprovalsComponent } from './admin/components/vendor-approvals/vendor-approvals.component';
import { BookingsOverviewComponent } from './admin/components/bookings-overview/bookings-overview.component';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';
import { PhotosManageComponent } from './vendor/components/photos-manage/photos-manage.component';

import { ForgotPasswordComponent } from './core/components/forgot-password/forgot-password.component';
import { ResetPasswordComponent } from './core/components/reset-password/reset-password.component';
import { MyWishlistComponent } from './customer/components/my-wishlist/my-wishlist.component';

import { ChangePasswordComponent } from './core/components/change-password/change-password.component';
import { ReviewsViewComponent } from './vendor/components/reviews-view/reviews-view.component';
import { SplashComponent } from './core/components/splash/splash.component';


import { MyReviewsComponent } from './customer/components/my-reviews/my-reviews.component';
import { UsersManageComponent } from './admin/components/users-manage/users-manage.component';

import { DocumentsManageComponent } from './vendor/components/documents-manage/documents-manage.component';

import { MyProfileComponent } from './shared/components/my-profile/my-profile.component';
import { VendorDirectoryComponent } from './admin/components/vendor-directory/vendor-directory.component';
import { SessionsManageComponent } from './shared/components/sessions-manage/sessions-manage.component';

import { ConversationsListComponent } from './shared/components/conversations-list/conversations-list.component';
import { ChatWindowComponent } from './shared/components/chat-window/chat-window.component';

import { AnalyticsComponent } from './vendor/components/analytics/analytics.component';


import { PrivacyPolicyComponent } from './core/components/privacy-policy/privacy-policy.component';
import { TermsOfServiceComponent } from './core/components/terms-of-service/terms-of-service.component';
import { RefundPolicyComponent } from './core/components/refund-policy/refund-policy.component';
import { CookiePolicyComponent } from './core/components/cookie-policy/cookie-policy.component';
import { ContactComponent } from './core/components/contact/contact.component';
import { CreateEventPostComponent } from './customer/components/create-event-post/create-event-post.component';
import { MyEventPostsComponent } from './customer/components/my-event-posts/my-event-posts.component';
import { EventPostsFeedComponent } from './vendor/components/event-posts-feed/event-posts-feed.component';


export const routes: Routes = [
  { path: '', component: SplashComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'verify-otp', component: OtpVerifyComponent },
  { path: 'vendor/photos', component: PhotosManageComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  { path: 'forgot-password', component: ForgotPasswordComponent },
  { path: 'reset-password', component: ResetPasswordComponent },
  { path: 'settings/change-password', component: ChangePasswordComponent, canActivate: [authGuard] },
  { path: 'sessions', component: SessionsManageComponent, canActivate: [authGuard] },
  { path: 'profile', component: MyProfileComponent, canActivate: [authGuard] },
  { path: 'admin/directory', component: VendorDirectoryComponent, canActivate: [authGuard, roleGuard(['admin'])] },
  { path: 'messages', component: ConversationsListComponent, canActivate: [authGuard] },
  { path: 'chat/booking/:bookingId', component: ChatWindowComponent, canActivate: [authGuard] },
  { path: 'chat/user/:userId', component: ChatWindowComponent, canActivate: [authGuard] },
  { path: 'privacy-policy', component: PrivacyPolicyComponent },
  { path: 'terms-of-service', component: TermsOfServiceComponent },
  { path: 'refund-policy', component: RefundPolicyComponent },
  { path: 'cookie-policy', component: CookiePolicyComponent },
  { path: 'contact', component: ContactComponent },


  // Customer routes
  { path: 'customer/home', component: HomeComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  { path: 'customer/vendor/:id', component: VendorDetailComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  { path: 'customer/bookings', component: MyBookingsComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  { path: 'customer/booking/:id', component: BookingDetailComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  { path: 'customer/wishlist', component: MyWishlistComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  { path: 'customer/reviews', component: MyReviewsComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  { path: 'customer/post/create', component: CreateEventPostComponent, canActivate: [authGuard, roleGuard(['customer'])] },
  { path: 'customer/my-posts', component: MyEventPostsComponent, canActivate: [authGuard, roleGuard(['customer'])] },


  // Vendor routes
  { path: 'vendor/dashboard', component: VendorDashboardComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  { path: 'vendor/profile', component: ProfileEditComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  { path: 'vendor/services', component: ServicesManageComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  { path: 'vendor/bookings', component: BookingsManageComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  { path: 'vendor/reviews', component: ReviewsViewComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  { path: 'vendor/documents', component: DocumentsManageComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  { path: 'vendor/analytics', component: AnalyticsComponent, canActivate: [authGuard, roleGuard(['vendor'])] },
  { path: 'vendor/event-posts', component: EventPostsFeedComponent, canActivate: [authGuard, roleGuard(['vendor'])] },

  // Admin routes
  { path: 'admin/dashboard', component: AdminDashboardComponent, canActivate: [authGuard, roleGuard(['admin'])] },
  { path: 'admin/vendors', component: VendorApprovalsComponent, canActivate: [authGuard, roleGuard(['admin'])] },
  { path: 'admin/bookings', component: BookingsOverviewComponent, canActivate: [authGuard, roleGuard(['admin'])] },
  { path: 'admin/users', component: UsersManageComponent, canActivate: [authGuard, roleGuard(['admin'])] },
];