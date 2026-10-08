import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { NavbarComponent } from '../navbar/navbar.component';
import { FooterComponent } from '../footer/footer.component';

interface SupportCategory {
  id: string;
  icon: string;
  title: string;
  description: string;
  color: string;
}

interface FAQ {
  id: number;
  category: string;
  question: string;
  answer: string;
  open?: boolean;
}

interface SupportTicket {
  id: string;
  subject: string;
  category: string;
  date: string;
  status: 'Open' | 'In Progress' | 'Resolved';
}

@Component({
  selector: 'app-help-support',
  imports: [
    CommonModule,
    FormsModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    NavbarComponent,
    FooterComponent
  ],
  templateUrl: './help-support.component.html',
  styleUrl: './help-support.component.scss'
})
export class HelpSupportComponent {

  // --------------------------------------------------
  // STATE
  // --------------------------------------------------

  searchTerm = '';

  selectedCategory = 'all';

  showReportForm = false;

  submittingTicket = false;

  loadingTickets = false;

  selectedFile: File | null = null;

  // --------------------------------------------------
  // REPORT FORM
  // --------------------------------------------------

  reportForm = {
    category: '',
    subject: '',
    description: '',
    bookingId: ''
  };

  // --------------------------------------------------
  // SUPPORT CATEGORIES
  // --------------------------------------------------

  categories: SupportCategory[] = [
    {
      id: 'booking',
      icon: 'event_available',
      title: 'Bookings & Events',
      description: 'Booking, cancellation and event-related help.',
      color: 'purple'
    },
    // {
    //   id: 'payment',
    //   icon: 'payments',
    //   title: 'Payments & Refunds',
    //   description: 'Payment failures, refunds and transactions.',
    //   color: 'gold'
    // },
    {
      id: 'account',
      icon: 'person',
      title: 'Account & Profile',
      description: 'Manage your account and profile settings.',
      color: 'blue'
    },
    {
      id: 'vendor',
      icon: 'storefront',
      title: 'Vendor Issues',
      description: 'Problems with vendors or vendor services.',
      color: 'orange'
    },
    {
      id: 'chat',
      icon: 'chat',
      title: 'Messages & Chat',
      description: 'Help with conversations and messaging.',
      color: 'green'
    },
    {
      id: 'security',
      icon: 'security',
      title: 'Security',
      description: 'Account security and suspicious activity.',
      color: 'red'
    },
    {
      id: 'technical',
      icon: 'build',
      title: 'Technical Issues',
      description: 'Website, app or technical problems.',
      color: 'cyan'
    },
    {
      id: 'report',
      icon: 'report_problem',
      title: 'Report a Problem',
      description: 'Report an issue or inappropriate behavior.',
      color: 'pink'
    }
  ];

  // --------------------------------------------------
  // FAQ DATA
  // --------------------------------------------------

  faqs: FAQ[] = [
    {
      id: 1,
      category: 'booking',
      question: 'How do I book a vendor?',
      answer:
        'Find the vendor you are interested in, select the service you need, choose your preferred date and time, and continue to booking. You can review the booking details before confirming your request.'
    },
    {
      id: 2,
      category: 'booking',
      question: 'Can I cancel my booking?',
      answer:
        'Yes, you can request cancellation from your bookings section. Cancellation and refund eligibility may depend on the booking status and the vendor’s cancellation policy.'
    },
    {
      id: 3,
      category: 'payment',
      question: 'What payment methods are supported?',
      answer:
        'Evenzoo uses secure online payment processing. Available payment methods are shown during checkout and may vary depending on your location and payment provider.'
    },
    {
      id: 4,
      category: 'payment',
      question: 'My payment failed. What should I do?',
      answer:
        'First check your bank or payment provider and make sure your internet connection is stable. If the amount was deducted but your booking was not confirmed, please contact support with your booking or payment details.'
    },
    {
      id: 5,
      category: 'payment',
      question: 'How long does a refund take?',
      answer:
        'Refund processing time depends on the payment method and banking provider. Once a refund is initiated, the amount may take several business days to appear in your account.'
    },
    {
      id: 6,
      category: 'account',
      question: 'How can I change my profile information?',
      answer:
        'Open your profile, choose Edit Profile, update the required information and save your changes.'
    },
    {
      id: 7,
      category: 'account',
      question: 'I forgot my password. How can I reset it?',
      answer:
        'Use the Forgot Password option on the login screen. Enter your registered email or phone number and follow the instructions to create a new password.'
    },
    {
      id: 8,
      category: 'vendor',
      question: 'How do I contact a vendor?',
      answer:
        'You can contact a vendor from their vendor profile using the available messaging or contact options.'
    },
    {
      id: 9,
      category: 'vendor',
      question: 'What should I do if a vendor does not respond?',
      answer:
        'You can send another message through Evenzoo. If the vendor remains unresponsive and you have an active booking, contact support and provide your booking details.'
    },
    {
      id: 10,
      category: 'chat',
      question: 'Why are my messages not loading?',
      answer:
        'Check your internet connection and refresh the conversation. If the issue continues, report it to support with the affected conversation and approximate time of the issue.'
    },
    {
      id: 11,
      category: 'security',
      question: 'What should I do if I see suspicious activity?',
      answer:
        'Change your password immediately and contact support. Never share your password, OTP, payment PIN or other sensitive security information with anyone.'
    },
    {
      id: 12,
      category: 'technical',
      question: 'The website is not loading correctly. What can I do?',
      answer:
        'Try refreshing the page, clearing your browser cache, checking your internet connection or trying another browser. If the issue persists, submit a support ticket.'
    }
  ];

  // --------------------------------------------------
  // TICKETS
  // --------------------------------------------------

  tickets: SupportTicket[] = [
    {
      id: 'EZ-1024',
      subject: 'Payment deducted but booking not confirmed',
      category: 'Payments',
      date: '02 Oct 2026',
      status: 'In Progress'
    },
    {
      id: 'EZ-1018',
      subject: 'Vendor did not respond',
      category: 'Vendor',
      date: '28 Sep 2026',
      status: 'Resolved'
    }
  ];

  ngOnInit(): void {
    this.loadTickets();
  }

  // --------------------------------------------------
  // FAQ FILTER
  // --------------------------------------------------

  get filteredFAQs(): FAQ[] {

    const search = this.searchTerm.trim().toLowerCase();

    return this.faqs.filter(faq => {

      const matchesCategory =
        this.selectedCategory === 'all' ||
        faq.category === this.selectedCategory;

      const matchesSearch =
        !search ||
        faq.question.toLowerCase().includes(search) ||
        faq.answer.toLowerCase().includes(search);

      return matchesCategory && matchesSearch;
    });
  }

  // --------------------------------------------------
  // CATEGORY FILTER
  // --------------------------------------------------

  selectCategory(category: string): void {

    this.selectedCategory = category;

    setTimeout(() => {
      document
        .getElementById('faq-section')
        ?.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
    }, 50);
  }

  // --------------------------------------------------
  // FAQ ACCORDION
  // --------------------------------------------------

  toggleFAQ(faq: FAQ): void {
    faq.open = !faq.open;
  }

  // --------------------------------------------------
  // CLEAR SEARCH
  // --------------------------------------------------

  clearSearch(): void {
    this.searchTerm = '';
    this.selectedCategory = 'all';
  }

  // --------------------------------------------------
  // REPORT FORM
  // --------------------------------------------------

  openReportForm(): void {
    this.showReportForm = true;

    setTimeout(() => {
      document
        .getElementById('report-form')
        ?.scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        });
    }, 50);
  }

  closeReportForm(): void {
    if (this.submittingTicket) {
      return;
    }

    this.showReportForm = false;
  }

  // --------------------------------------------------
  // FILE UPLOAD
  // --------------------------------------------------

  onFileSelected(event: Event): void {

    const input = event.target as HTMLInputElement;

    if (!input.files || input.files.length === 0) {
      return;
    }

    const file = input.files[0];

    // 10 MB limit
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10 MB.');
      input.value = '';
      return;
    }

    this.selectedFile = file;
  }

  removeFile(): void {
    this.selectedFile = null;
  }

  // --------------------------------------------------
  // SUBMIT TICKET
  // --------------------------------------------------

  submitTicket(): void {

    if (
      !this.reportForm.category ||
      !this.reportForm.subject.trim() ||
      !this.reportForm.description.trim()
    ) {
      return;
    }

    this.submittingTicket = true;

    /*
     * API INTEGRATION:
     *
     * Replace this timeout with your actual service:
     *
     * this.supportService.createTicket(formData).subscribe({
     *   next: () => {...},
     *   error: () => {...}
     * });
     */

    setTimeout(() => {

      const newTicket: SupportTicket = {
        id: `EZ-${Math.floor(1000 + Math.random() * 9000)}`,
        subject: this.reportForm.subject,
        category: this.reportForm.category,
        date: new Date().toLocaleDateString('en-IN', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        }),
        status: 'Open'
      };

      this.tickets.unshift(newTicket);

      this.submittingTicket = false;

      this.showReportForm = false;

      this.resetReportForm();

      alert(
        `Your support request has been submitted.\nTicket ID: ${newTicket.id}`
      );

    }, 1200);
  }

  // --------------------------------------------------
  // RESET FORM
  // --------------------------------------------------

  resetReportForm(): void {

    this.reportForm = {
      category: '',
      subject: '',
      description: '',
      bookingId: ''
    };

    this.selectedFile = null;
  }

  // --------------------------------------------------
  // TICKET LOADING
  // --------------------------------------------------

  loadTickets(): void {

    this.loadingTickets = true;

    /*
     * Replace this with:
     *
     * this.supportService.getMyTickets().subscribe(...)
     */

    setTimeout(() => {
      this.loadingTickets = false;
    }, 500);
  }

  // --------------------------------------------------
  // CONTACT ACTIONS
  // --------------------------------------------------

  startChat(): void {
    // Navigate to your support chat component.
    // Example:
    // this.router.navigate(['/support-chat']);

    console.log('Opening support chat...');
  }

  emailSupport(): void {

    window.location.href =
      'mailto:support@evenzoo.com?subject=Evenzoo Support Request';
  }

  callSupport(): void {

    window.location.href =
      'tel:+919999999999';
  }

  viewTicket(ticket: SupportTicket): void {

    console.log('View ticket:', ticket.id);

    // Example:
    // this.router.navigate(['/support/tickets', ticket.id]);
  }

  // --------------------------------------------------
  // HELPERS
  // --------------------------------------------------

  getStatusClass(status: string): string {

    switch (status) {

      case 'Open':
        return 'status-open';

      case 'In Progress':
        return 'status-progress';

      case 'Resolved':
        return 'status-resolved';

      default:
        return '';
    }
  }

  trackByFaq(index: number, faq: FAQ): number {
    return faq.id;
  }

  trackByTicket(index: number, ticket: SupportTicket): string {
    return ticket.id;
  }

}
