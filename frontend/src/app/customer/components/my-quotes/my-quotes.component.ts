import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink  } from '@angular/router';

import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { FormsModule } from '@angular/forms';

import { QuoteService, Quote } from '../../../core/services/quote.service';
import { VendorService } from '../../../core/services/vendor.service';
import { Category } from '../../../core/models/vendor.model';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { NativeDateModule } from '@angular/material/core';
import { MatNativeDateModule } from '@angular/material/core';
import { MatInputModule } from '@angular/material/input';

interface PostSummary {
  event_post_id: number | null;
  post_title: string;
  event_date: string | null;
  is_expired: boolean;
  quote_count: number;
  lowest_quote: number | null;
  highest_quote: number | null;
}


@Component({
  selector: 'app-my-quotes',
  standalone: true,
  imports: [
    CommonModule,
    MatDatepickerModule,
    MatInputModule,
    NativeDateModule,
    FormsModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatCheckboxModule,
    MatProgressSpinnerModule,
    NavbarComponent,
    MatTooltipModule,
    RouterLink,
    MatNativeDateModule
  ],
  templateUrl: './my-quotes.component.html',
  styleUrl: './my-quotes.component.scss'
})
export class MyQuotesComponent implements OnInit {

  // =========================================================
  // POSTS
  // =========================================================

  postSummaries: PostSummary[] = [];

  /*
    undefined = no post selected yet
    null      = direct enquiries bucket
    number    = selected event post
  */
  selectedPostId: number | null | undefined = undefined;


  // =========================================================
  // QUOTES
  // =========================================================

  quotes: Quote[] = [];

  categories: Category[] = [];

  selectedCategoryId: number | null = null;

  sortOrder: 'best' | 'worst' = 'best';
  loading!:boolean;


  // =========================================================
  // LOADING
  // =========================================================

  loadingSummary = true;

  loadingQuotes = false;


  // =========================================================
  // COMPARE
  // =========================================================

  selectedForCompare: number[] = [];


  // =========================================================
  // MAIN QUOTE TABS
  // =========================================================

  /*
    posts   = active event post quotes
    direct  = direct vendor quotes
    expired = expired event post quotes
  */
  quoteView: 'posts' | 'direct' | 'expired' = 'posts';


  // Number of active event posts
  activePostCount = 0;

  // Number of expired event posts
  expiredPostCount = 0;
  useCustomRange = false;
  fromDate: Date | null = null;
  toDate: Date | null = null;


  // =========================================================
  // CONSTRUCTOR
  // =========================================================

  constructor(
    private quoteService: QuoteService,
    private vendorService: VendorService,
    private router: Router,
    private route: ActivatedRoute
  ) {}


  // =========================================================
  // INITIAL LOAD
  // =========================================================

  ngOnInit(): void {

    // Load categories for filter dropdown
    this.vendorService.getCategories().subscribe({
      next: (data) => {
        this.categories = data;
      },

      error: (error) => {
        console.error('Failed to load categories:', error);
        this.categories = [];
      }
    });


    // Load event post summary
    this.loadSummary();


    // Check if a post_id was passed in URL
    const postIdParam = this.route.snapshot.queryParamMap.get('post_id');

    if (postIdParam) {

      const postId = Number(postIdParam);

      if (!Number.isNaN(postId)) {
        this.selectedPostId = postId;
      }
    }
  }


  // =========================================================
  // LOAD POST SUMMARY
  // =========================================================

  loadSummary(): void {

    this.loadingSummary = true;

    this.quoteService.getQuoteSummaryByPost().subscribe({

      next: (data) => {

        this.postSummaries = data ?? [];


        // -----------------------------------------------------
        // Calculate active and expired counts
        // -----------------------------------------------------

        this.activePostCount = this.postSummaries.filter(
          post => !post.is_expired
        ).length;


        this.expiredPostCount = this.postSummaries.filter(
          post => post.is_expired
        ).length;


        this.loadingSummary = false;


        // -----------------------------------------------------
        // If a post was already selected, load its quotes
        // -----------------------------------------------------

        if (this.selectedPostId !== undefined) {

          this.loadQuotesForPost(this.selectedPostId);
        }
      },

      error: (error) => {

        console.error(
          'Failed to load quote summary:',
          error
        );

        this.postSummaries = [];

        this.activePostCount = 0;

        this.expiredPostCount = 0;

        this.loadingSummary = false;
      }

    });
  }


  // =========================================================
  // SELECT POST
  // =========================================================

  selectPost(postId: number | null): void {

    this.selectedPostId = postId;

    // Clear previous comparison selections
    this.selectedForCompare = [];

    // Load quotes for selected post
    this.loadQuotesForPost(postId);
  }


  // =========================================================
  // BACK TO POST LIST
  // =========================================================

  backToPostList(): void {

    this.selectedPostId = undefined;

    this.quotes = [];

    this.selectedForCompare = [];

    this.selectedCategoryId = null;

    this.sortOrder = 'best';
  }


  // =========================================================
  // LOAD QUOTES FOR SELECTED POST
  // =========================================================
loadQuotesForPost(postId: number | null): void {
  this.loadingQuotes = true;

  const from = this.useCustomRange && this.fromDate ? this.fromDate.toISOString() : undefined;
  const to = this.useCustomRange && this.toDate ? this.toDate.toISOString() : undefined;

   this.quoteService.getMyQuotes(this.selectedCategoryId || undefined, postId || undefined, 30, from, to).subscribe({
    next: (data) => {
      this.quotes = data ?? [];

      // When viewing an event post,
      // only event-post quotes should be displayed.
      if (postId !== null && postId !== undefined) {
        this.quotes = this.quotes.filter(
          quote =>
            quote.event_post_id === postId
        );
      }

      this.loadingQuotes = false;
    },

    error: (error) => {
      console.error(
        'Failed to load quotes:',
        error
      );

      this.quotes = [];
      this.loadingQuotes = false;
    }
  });
}
loadDirectVendorQuotes(): void {
  this.loadingQuotes = true;

  this.quoteService.getMyQuotes(
    undefined,
    undefined
  ).subscribe({
    next: (data) => {
      const allQuotes = data ?? [];

      this.quotes = allQuotes.filter(
        quote =>
          quote.event_post_id === null ||
          quote.event_post_id === undefined
      );

      this.loadingQuotes = false;
    },

    error: (error) => {
      console.error(
        'Failed to load direct vendor quotes:',
        error
      );

      this.quotes = [];
      this.loadingQuotes = false;
    }
  });
}
loadEventPostQuotes(): void {
  this.loadingQuotes = true;

  this.quoteService.getMyQuotes(
    undefined,
    undefined
  ).subscribe({
    next: (data) => {
      const allQuotes = data ?? [];

      this.quotes = allQuotes.filter(
        quote =>
          quote.event_post_id !== null &&
          quote.event_post_id !== undefined
      );

      this.loadingQuotes = false;
    },

    error: (error) => {
      console.error(
        'Failed to load event post quotes:',
        error
      );

      this.quotes = [];
      this.loadingQuotes = false;
    }
  });
}

  // =========================================================
  // CATEGORY CHANGE
  // =========================================================

  onCategoryChange(): void {

    if (this.selectedPostId !== undefined) {

      this.loadQuotesForPost(
        this.selectedPostId
      );
    }
  }


  // =========================================================
  // SORT QUOTES
  // =========================================================

  get sortedQuotes(): Quote[] {

    /*
      Quotes WITH price
      -----------------
      These are sorted according to best/worst.

      Quotes WITHOUT price
      --------------------
      These always remain at the bottom.
    */

    const withAmount = this.quotes.filter(
      q =>
        q.quoted_amount !== null &&
        q.quoted_amount !== undefined &&
        q.quoted_amount > 0
    );


    const withoutAmount = this.quotes.filter(
      q =>
        !q.quoted_amount ||
        q.quoted_amount === 0
    );


    // Sort priced quotes
    withAmount.sort((a, b) => {

      const amountA = a.quoted_amount || 0;

      const amountB = b.quoted_amount || 0;


      if (this.sortOrder === 'best') {

        // Lowest price first
        return amountA - amountB;

      } else {

        // Highest price first
        return amountB - amountA;
      }
    });


    // Return priced quotes first,
    // pending-price quotes afterwards
    return [
      ...withAmount,
      ...withoutAmount
    ];
  }


  // =========================================================
  // TOGGLE SORT
  // =========================================================

  toggleSort(): void {

    this.sortOrder =
      this.sortOrder === 'best'
        ? 'worst'
        : 'best';
  }


  // =========================================================
  // COMPARE SELECTION
  // =========================================================

  toggleCompareSelect(quoteId: number): void {

    const idx =
      this.selectedForCompare.indexOf(quoteId);


    // Already selected
    if (idx > -1) {

      this.selectedForCompare.splice(
        idx,
        1
      );

      return;
    }


    // Maximum 4 vendors
    if (this.selectedForCompare.length >= 4) {

      alert(
        'You can compare up to 4 quoted vendors at a time'
      );

      return;
    }


    // Add vendor
    this.selectedForCompare.push(
      quoteId
    );
  }


  // =========================================================
  // VENDOR COMPARISON
  // =========================================================

  goToVendorComparison(): void {

    const vendorIds = this.quotes
      .filter(q =>
        this.selectedForCompare.includes(q.id)
      )
      .map(q => q.vendor_id);


    // Need at least 2 vendors
    if (vendorIds.length < 2) {

      alert(
        'Select at least 2 quotes to compare vendors'
      );

      return;
    }


    this.router.navigate(
      ['/browse/compare'],
      {
        queryParams: {
          ids: vendorIds.join(',')
        }
      }
    );
  }


  // =========================================================
  // ACCEPT QUOTE
  // =========================================================

  accept(quote: Quote): void {

    const amount =
      quote.quoted_amount ?? 0;


    const vendorName =
      quote.vendor_business_name || 'this vendor';


    const confirmed = confirm(
      `Accept this quote of ₹${amount} from ${vendorName}?`
    );


    if (!confirmed) {
      return;
    }


    this.quoteService.updateStatus(
      quote.id,
      'accepted'
    ).subscribe({

      next: () => {

        this.loadQuotesForPost(
          this.selectedPostId!
        );
      },

      error: (error) => {

        console.error(
          'Failed to accept quote:',
          error
        );

        alert(
          'Failed to accept the quote. Please try again.'
        );
      }

    });
  }


  // =========================================================
  // DECLINE QUOTE
  // =========================================================

  decline(quote: Quote): void {

    this.quoteService.updateStatus(
      quote.id,
      'declined'
    ).subscribe({

      next: () => {

        this.loadQuotesForPost(
          this.selectedPostId!
        );
      },

      error: (error) => {

        console.error(
          'Failed to decline quote:',
          error
        );

        alert(
          'Failed to decline the quote. Please try again.'
        );
      }

    });
  }


  // =========================================================
  // STATUS COLOR
  // =========================================================

  statusColor(status: string): string {

    const colors: Record<string, string> = {

      pending: '#f5a623',

      accepted: '#16a34a',

      declined: '#dc2626',

      withdrawn: '#94a3b8',

      cancelled: '#64748b',

      completed: '#2563eb'
    };


    return (
      colors[status?.toLowerCase()] ||
      '#64748b'
    );
  }


  // =========================================================
  // CHECK EXPIRED POSTS
  // =========================================================

  get hasAnyExpired(): boolean {

    return this.expiredPostCount > 0;
  }


  // =========================================================
  // CHECK ACTIVE POSTS
  // =========================================================

  get hasAnyActivePosts(): boolean {

    return this.activePostCount > 0;
  }


  // =========================================================
  // SWITCH MAIN TAB
  // =========================================================
switchQuoteView(
  view: 'posts' | 'direct' | 'expired'
): void {

  this.quoteView = view;

  // Reset selected post
  this.selectedPostId = undefined;

  // Reset quote-related state
  this.quotes = [];
  this.selectedForCompare = [];
  this.selectedCategoryId = null;
  this.sortOrder = 'best';

  // Load correct data for selected tab
  if (view === 'direct') {
    this.loadDirectVendorQuotes();
    return;
  }

  if (view === 'posts') {
    this.loadEventPostQuotes();
    return;
  }

  // Expired posts
  // are selected from postSummaries,
  // so don't load general quotes here.
}  get eventPostQuotes(): Quote[] {
    return this.quotes.filter(
      quote =>
        quote.event_post_id !== null &&
        quote.event_post_id !== undefined
    );
  }

  get directVendorQuotes(): Quote[] {
    return this.quotes.filter(
      quote =>
        quote.event_post_id === null ||
        quote.event_post_id === undefined
    );
  }


toggleCustomRange() {
  this.useCustomRange = !this.useCustomRange;
  if (!this.useCustomRange) {
    this.fromDate = null;
    this.toDate = null;
    this.loadQuotesForPost(this.selectedPostId!);
  }
}

onDateRangeChange() {
  if (this.fromDate || this.toDate) {
    this.loadQuotesForPost(this.selectedPostId!);
  }
}
}