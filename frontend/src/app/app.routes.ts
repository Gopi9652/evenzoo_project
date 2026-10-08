import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [

  // =========================================================
  // PUBLIC ROUTES
  // =========================================================

  {
    path: '',
    loadComponent: () =>
      import('./core/components/splash/splash.component')
        .then(m => m.SplashComponent),
  },

  {
    path: 'login',
    loadComponent: () =>
      import('./core/components/login/login.component')
        .then(m => m.LoginComponent),
  },

  {
    path: 'register',
    loadComponent: () =>
      import('./core/components/register/register.component')
        .then(m => m.RegisterComponent),
  },

  {
    path: 'verify-otp',
    loadComponent: () =>
      import('./core/components/otp-verify/otp-verify.component')
        .then(m => m.OtpVerifyComponent),
  },

  {
    path: 'forgot-password',
    loadComponent: () =>
      import('./core/components/forgot-password/forgot-password.component')
        .then(m => m.ForgotPasswordComponent),
  },

  {
    path: 'reset-password',
    loadComponent: () =>
      import('./core/components/reset-password/reset-password.component')
        .then(m => m.ResetPasswordComponent),
  },

  {
    path: 'settings/confirm-email',
    loadComponent: () =>
      import('./core/components/confirm-email/confirm-email.component')
        .then(m => m.ConfirmEmailComponent),
  },

  // =========================================================
  // PUBLIC BROWSING
  // =========================================================

  {
    path: 'browse',
    loadComponent: () =>
      import('./customer/components/home/home.component')
        .then(m => m.HomeComponent),
  },

  {
    path: 'browse/vendor/:slug',
    loadComponent: () =>
      import('./customer/components/vendor-detail/vendor-detail.component')
        .then(m => m.VendorDetailComponent),
  },

  {
    path: 'browse/compare',
    loadComponent: () =>
      import('./customer/components/vendor-compare/vendor-compare.component')
        .then(m => m.VendorCompareComponent),
  },

  {
    path: 'nearby',
    loadComponent: () =>
      import('./customer/components/nearby-vendors/nearby-vendors.component')
        .then(m => m.NearbyVendorsComponent),
  },

  // =========================================================
  // LEGACY CUSTOMER URL REDIRECTS
  // =========================================================

  {
    path: 'customer/home',
    redirectTo: 'browse',
    pathMatch: 'full',
  },

  {
    path: 'customer/vendor/:id',
    redirectTo: 'browse/vendor/:id',
    pathMatch: 'full',
  },

  {
    path: 'customer/compare',
    redirectTo: 'browse/compare',
    pathMatch: 'full',
  },

  // =========================================================
  // AUTHENTICATED SHARED ROUTES
  // =========================================================

  {
    path: 'settings/change-password',
    loadComponent: () =>
      import('./core/components/change-password/change-password.component')
        .then(m => m.ChangePasswordComponent),
    canActivate: [authGuard],
  },

  {
    path: 'sessions',
    loadComponent: () =>
      import('./shared/components/sessions-manage/sessions-manage.component')
        .then(m => m.SessionsManageComponent),
    canActivate: [authGuard],
  },

  {
    path: 'profile',
    loadComponent: () =>
      import('./shared/components/my-profile/my-profile.component')
        .then(m => m.MyProfileComponent),
    canActivate: [authGuard],
  },

  {
    path: 'messages',
    loadComponent: () =>
      import('./shared/components/conversations-list/conversations-list.component')
        .then(m => m.ConversationsListComponent),
    canActivate: [authGuard],
  },

  {
    path: 'chat/booking/:bookingId',
    loadComponent: () =>
      import('./shared/components/chat-window/chat-window.component')
        .then(m => m.ChatWindowComponent),
    canActivate: [authGuard],
    runGuardsAndResolvers: 'always',
  },

  {
    path: 'chat/user/:userId',
    loadComponent: () =>
      import('./shared/components/chat-window/chat-window.component')
        .then(m => m.ChatWindowComponent),
    canActivate: [authGuard],
    runGuardsAndResolvers: 'always',
  },

  {
    path: 'settings/privacy',
    loadComponent: () =>
      import('./shared/components/privacy-settings/privacy-settings.component')
        .then(m => m.PrivacySettingsComponent),
    canActivate: [authGuard],
  },

  {
    path: 'help-support',
    loadComponent: () =>
      import('./shared/components/help-support/help-support.component')
        .then(m => m.HelpSupportComponent),
    canActivate: [authGuard],
  },

  // =========================================================
  // LEGAL / INFORMATIONAL
  // =========================================================

  {
    path: 'privacy-policy',
    loadComponent: () =>
      import('./core/components/privacy-policy/privacy-policy.component')
        .then(m => m.PrivacyPolicyComponent),
  },

  {
    path: 'terms-of-service',
    loadComponent: () =>
      import('./core/components/terms-of-service/terms-of-service.component')
        .then(m => m.TermsOfServiceComponent),
  },

  {
    path: 'refund-policy',
    loadComponent: () =>
      import('./core/components/refund-policy/refund-policy.component')
        .then(m => m.RefundPolicyComponent),
  },

  {
    path: 'cookie-policy',
    loadComponent: () =>
      import('./core/components/cookie-policy/cookie-policy.component')
        .then(m => m.CookiePolicyComponent),
  },

  {
    path: 'contact',
    loadComponent: () =>
      import('./core/components/contact/contact.component')
        .then(m => m.ContactComponent),
  },

  // =========================================================
  // CUSTOMER MODULE
  // =========================================================

  {
    path: 'customer',
    loadChildren: () =>
      import('./customer/customer.routes')
        .then(m => m.customerRoutes),
    canActivateChild: [
      authGuard,
      roleGuard(['customer']),
    ],
  },

  // =========================================================
  // CUSTOMER QUOTES
  // =========================================================

  {
    path: 'customer/quotes',
    loadComponent: () =>
      import('./customer/components/my-quotes/my-quotes.component')
        .then(m => m.MyQuotesComponent),
    canActivate: [
      authGuard,
      roleGuard(['customer']),
    ],
  },

  // =========================================================
  // VENDOR MODULE
  // =========================================================

  {
    path: 'vendor',
    loadChildren: () =>
      import('./vendor/vendor.routes')
        .then(m => m.vendorRoutes),
    canActivateChild: [
      authGuard,
      roleGuard(['vendor']),
    ],
  },

  // =========================================================
  // VENDOR QUOTES
  // =========================================================

  {
    path: 'vendor/quotes',
    loadComponent: () =>
      import('./vendor/components/quotes-received/quotes-received.component')
        .then(m => m.QuotesReceivedComponent),
    canActivate: [
      authGuard,
      roleGuard(['vendor']),
    ],
  },

  // =========================================================
  // ADMIN MODULE
  // =========================================================

  {
    path: 'admin',
    loadChildren: () =>
      import('./admin/admin.routes')
        .then(m => m.adminRoutes),
    canActivateChild: [
      authGuard,
      roleGuard(['admin']),
    ],
  },

  // =========================================================
  // FALLBACK
  // =========================================================

  {
    path: '**',
    redirectTo: '',
  },
];