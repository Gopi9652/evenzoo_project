import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatOptionModule } from '@angular/material/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';

import { QuoteService } from '../../../core/services/quote.service';
import { VendorService } from '../../../core/services/vendor.service';
import { Category } from '../../../core/models/vendor.model';

import { RespondQuoteDialogComponent } from '../../../shared/components/respond-quote-dialog/respond-quote-dialog.component';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { MatInputModule } from '@angular/material/input';

interface ReceivedQuote {
  id: number;

  customer_id?: number;
  customer_name?: string;

  event_type_name?: string;

  event_post_id?: number;
  event_post_title?: string;

  category_id?: number;
  category_name?: string;

  message?: string;

  quoted_amount?: number | null;

  status: string;

  created_at?: string;
  responded_at?: string;
}


interface QuoteCategory {
  id: number;
  name: string;
  icon?: string;
}


@Component({
  selector: 'app-quotes-received',

  standalone: true,

  imports: [
    CommonModule,
    FormsModule,
    MatInputModule,

    MatButtonModule,
    MatIconModule,

    MatSelectModule,
    MatFormFieldModule,

    MatDatepickerModule,
    MatNativeDateModule,
    MatOptionModule,

    MatProgressSpinnerModule,

    MatDialogModule,

    NavbarComponent,
  ],

  templateUrl: './quotes-received.component.html',

  styleUrl: './quotes-received.component.scss'
})
export class QuotesReceivedComponent implements OnInit {


  // =========================================================
  // QUOTES
  // =========================================================

  quotes: ReceivedQuote[] = [];

  pendingQuotes: ReceivedQuote[] = [];

  respondedQuotes: ReceivedQuote[] = [];


  // =========================================================
  // CATEGORY FILTER
  // =========================================================

  selectedCategoryId: number | null = null;

  categories: QuoteCategory[] = [];


  // =========================================================
  // DATE FILTER
  // =========================================================

  useCustomRange = false;

  fromDate: Date | null = null;

  toDate: Date | null = null;


  // =========================================================
  // SORT
  // =========================================================

  sortOrder: 'best' | 'worst' = 'best';


  // =========================================================
  // LOADING
  // =========================================================

  loading = false;


  // =========================================================
  // TABS
  // =========================================================

  activeTab: 'requests' | 'responses' = 'requests';


  // =========================================================
  // CONSTRUCTOR
  // =========================================================

  constructor(
    private quoteService: QuoteService,
    private vendorService: VendorService,
    private dialog: MatDialog
  ) {}


  // =========================================================
  // INIT
  // =========================================================

  ngOnInit(): void {

    // Load categories for category dropdown
    this.vendorService.getCategories().subscribe({
      next: (data: Category[]) => {

        this.categories = (data ?? []).map((category: Category) => ({
          id: category.id,
          name: category.name,
          icon: this.getCategoryIcon(category.name)
        }));

      },

      error: (error) => {

        console.error(
          'Failed to load categories:',
          error
        );

        // Fallback:
        // categories can still be built from quote data
        this.categories = [];

      }
    });


    // Load vendor quotes
    this.loadReceivedQuotes();

  }


  // =========================================================
  // LOAD RECEIVED QUOTES
  // =========================================================

  loadReceivedQuotes(): void {

    this.loading = true;


    /*
     * Send filters to backend.
     *
     * When custom range is disabled:
     *
     *     days = 30
     *
     * When custom range is enabled:
     *
     *     from = selected From date
     *     to   = selected To date
     */

    const from =
      this.useCustomRange && this.fromDate
        ? this.toDateStartISOString(this.fromDate)
        : undefined;


    const to =
      this.useCustomRange && this.toDate
        ? this.toDateEndISOString(this.toDate)
        : undefined;


    this.quoteService
      .getVendorReceivedQuotes(
        this.selectedCategoryId || undefined,
        30,
        from,
        to
      )
      .subscribe({

        next: (response: ReceivedQuote[]) => {

          this.quotes = response ?? [];


          // -------------------------------------------------
          // REQUESTS WAITING FOR VENDOR RESPONSE
          // -------------------------------------------------

          this.pendingQuotes =
            this.quotes.filter(
              quote =>
                quote.status?.toLowerCase() === 'pending' &&
                this.hasNoAmount(quote)
            );


          // -------------------------------------------------
          // QUOTES WHERE VENDOR ALREADY RESPONDED
          // -------------------------------------------------

          this.respondedQuotes =
            this.quotes.filter(
              quote =>
                !this.hasNoAmount(quote)
            );


          // -------------------------------------------------
          // FALLBACK CATEGORY LIST
          // -------------------------------------------------
          //
          // If VendorService did not return categories,
          // build them from received quotes.
          //

          if (this.categories.length === 0) {
            this.buildCategories();
          }


          this.loading = false;

        },


        error: (error) => {

          console.error(
            'Failed to load received quotes:',
            error
          );


          this.quotes = [];

          this.pendingQuotes = [];

          this.respondedQuotes = [];


          this.loading = false;

        }

      });

  }


  // =========================================================
  // BUILD CATEGORY FILTER OPTIONS
  // =========================================================

  buildCategories(): void {

    const categoryMap =
      new Map<number, QuoteCategory>();


    this.quotes.forEach(quote => {

      if (
        quote.category_id !== undefined &&
        quote.category_id !== null &&
        quote.category_name
      ) {

        if (
          !categoryMap.has(
            quote.category_id
          )
        ) {

          categoryMap.set(
            quote.category_id,
            {
              id: quote.category_id,

              name: quote.category_name,

              icon:
                this.getCategoryIcon(
                  quote.category_name
                )
            }
          );

        }

      }

    });


    this.categories =
      Array.from(
        categoryMap.values()
      ).sort(
        (a, b) =>
          a.name.localeCompare(b.name)
      );

  }


  // =========================================================
  // CATEGORY ICON
  // =========================================================

  getCategoryIcon(
    categoryName?: string
  ): string {

    const name =
      categoryName?.toLowerCase() ?? '';


    if (name.includes('photo')) {
      return '📸';
    }


    if (name.includes('decor')) {
      return '🎨';
    }


    if (name.includes('catering')) {
      return '🍽️';
    }


    if (name.includes('music')) {
      return '🎵';
    }


    if (name.includes('venue')) {
      return '🏛️';
    }


    if (name.includes('makeup')) {
      return '💄';
    }


    if (name.includes('mehndi')) {
      return '🌿';
    }


    if (name.includes('flower')) {
      return '🌸';
    }


    if (name.includes('cake')) {
      return '🎂';
    }


    if (name.includes('dj')) {
      return '🎧';
    }


    return '📌';

  }


  // =========================================================
  // FILTERED PENDING QUOTES
  // =========================================================

  get filteredPendingQuotes(): ReceivedQuote[] {

    let result =
      [...this.pendingQuotes];


    // -------------------------------------------------------
    // CATEGORY
    // -------------------------------------------------------

    if (
      this.selectedCategoryId !== null
    ) {

      result =
        result.filter(
          quote =>
            quote.category_id ===
            this.selectedCategoryId
        );

    }


    // -------------------------------------------------------
    // DATE
    // -------------------------------------------------------

    result =
      this.filterByDate(result);


    // -------------------------------------------------------
    // REQUESTS = NEWEST FIRST
    // -------------------------------------------------------

    result.sort(
      (a, b) =>
        this.getDateValue(
          b.created_at
        ) -
        this.getDateValue(
          a.created_at
        )
    );


    return result;

  }


  // =========================================================
  // FILTERED RESPONDED QUOTES
  // =========================================================

  get filteredRespondedQuotes(): ReceivedQuote[] {

    let result =
      [...this.respondedQuotes];


    // -------------------------------------------------------
    // CATEGORY
    // -------------------------------------------------------

    if (
      this.selectedCategoryId !== null
    ) {

      result =
        result.filter(
          quote =>
            quote.category_id ===
            this.selectedCategoryId
        );

    }


    // -------------------------------------------------------
    // DATE
    // -------------------------------------------------------

    result =
      this.filterByDate(result);


    // -------------------------------------------------------
    // PRICE SORT
    // -------------------------------------------------------

    result.sort(
      (a, b) => {

        const priceA =
          Number(
            a.quoted_amount ?? 0
          );


        const priceB =
          Number(
            b.quoted_amount ?? 0
          );


        // Best = highest quoted price first
        if (
          this.sortOrder === 'best'
        ) {

          return priceB - priceA;

        }


        // Worst = lowest quoted price first
        return priceA - priceB;

      }
    );


    return result;

  }


  // =========================================================
  // DATE FILTER
  // =========================================================

  private filterByDate(
    quotes: ReceivedQuote[]
  ): ReceivedQuote[] {


    // =======================================================
    // LAST 30 DAYS
    // =======================================================

    if (!this.useCustomRange) {

      const today =
        new Date();


      today.setHours(
        23,
        59,
        59,
        999
      );


      const thirtyDaysAgo =
        new Date(today);


      thirtyDaysAgo.setDate(
        thirtyDaysAgo.getDate() - 30
      );


      thirtyDaysAgo.setHours(
        0,
        0,
        0,
        0
      );


      return quotes.filter(
        quote => {

          if (!quote.created_at) {
            return false;
          }


          const quoteDate =
            new Date(
              quote.created_at
            );


          return (
            quoteDate >=
              thirtyDaysAgo &&
            quoteDate <=
              today
          );

        }
      );

    }


    // =======================================================
    // CUSTOM RANGE
    // =======================================================

    let from: Date | null = null;

    let to: Date | null = null;


    // -------------------------------------------------------
    // FROM
    // -------------------------------------------------------

    if (this.fromDate) {

      from =
        new Date(
          this.fromDate
        );


      from.setHours(
        0,
        0,
        0,
        0
      );

    }


    // -------------------------------------------------------
    // TO
    // -------------------------------------------------------

    if (this.toDate) {

      to =
        new Date(
          this.toDate
        );


      to.setHours(
        23,
        59,
        59,
        999
      );

    }


    // -------------------------------------------------------
    // NO CUSTOM DATE
    // -------------------------------------------------------

    if (!from && !to) {

      return quotes;

    }


    // -------------------------------------------------------
    // FILTER
    // -------------------------------------------------------

    return quotes.filter(
      quote => {

        if (!quote.created_at) {
          return false;
        }


        const quoteDate =
          new Date(
            quote.created_at
          );


        if (
          from &&
          quoteDate < from
        ) {

          return false;

        }


        if (
          to &&
          quoteDate > to
        ) {

          return false;

        }


        return true;

      }
    );

  }


  // =========================================================
  // DATE VALUE
  // =========================================================

  private getDateValue(
    date?: string
  ): number {

    if (!date) {
      return 0;
    }


    const timestamp =
      new Date(date).getTime();


    return Number.isNaN(timestamp)
      ? 0
      : timestamp;

  }


  // =========================================================
  // FROM DATE → ISO
  // =========================================================

  private toDateStartISOString(
    date: Date
  ): string {

    const value =
      new Date(date);


    value.setHours(
      0,
      0,
      0,
      0
    );


    return value.toISOString();

  }


  // =========================================================
  // TO DATE → ISO
  // =========================================================

  private toDateEndISOString(
    date: Date
  ): string {

    const value =
      new Date(date);


    value.setHours(
      23,
      59,
      59,
      999
    );


    return value.toISOString();

  }


  // =========================================================
  // CATEGORY CHANGE
  // =========================================================

  onCategoryChange(): void {

    /*
     * Category is sent to the backend.
     *
     * The filtered getters also apply the category locally,
     * so the UI remains consistent.
     */

    this.loadReceivedQuotes();

  }


  // =========================================================
  // DATE RANGE CHANGE
  // =========================================================

  onDateRangeChange(): void {

    /*
     * Do not make a request until at least
     * one date has actually been selected.
     */

    if (
      this.fromDate ||
      this.toDate
    ) {

      this.loadReceivedQuotes();

    }

  }


  // =========================================================
  // CUSTOM RANGE TOGGLE
  // =========================================================

  toggleCustomRange(): void {

    this.useCustomRange =
      !this.useCustomRange;


    if (!this.useCustomRange) {

      this.fromDate = null;

      this.toDate = null;

      this.loadReceivedQuotes();

    }

  }


  // =========================================================
  // SORT TOGGLE
  // =========================================================

  toggleSort(): void {

    this.sortOrder =
      this.sortOrder === 'best'
        ? 'worst'
        : 'best';

  }


  // =========================================================
  // RESPOND TO QUOTE
  // =========================================================

  respond(
    quote: ReceivedQuote
  ): void {

    const dialogRef =
      this.dialog.open(
        RespondQuoteDialogComponent,
        {
          width: '460px',

          maxWidth: '95vw',

          data: {

            quoteId:
              quote.id,

            customerName:
              quote.customer_name,

            eventTitle:
              quote.event_post_title,

            categoryName:
              quote.category_name,

            existingMessage:
              quote.message

          }

        }
      );


    dialogRef
      .afterClosed()
      .subscribe(result => {

        if (result) {

          this.loadReceivedQuotes();

        }

      });

  }


  // =========================================================
  // DIRECT RESPONSE METHOD
  // =========================================================

  respondToQuote(
    quote: ReceivedQuote
  ): void {

    const price =
      prompt(
        `Enter your price for ${quote.customer_name}:`
      );


    if (
      !price ||
      isNaN(Number(price)) ||
      Number(price) <= 0
    ) {

      return;

    }


    const message =
      prompt(
        'Optional message:'
      ) || undefined;


    this.quoteService
      .respondToQuote(
        quote.id,
        Number(price),
        message
      )
      .subscribe({

        next: () => {

          alert(
            'Quote sent!'
          );


          this.loadReceivedQuotes();

        },


        error: (err) => {

          alert(
            err.error?.detail ||
            'Failed to respond'
          );

        }

      });

  }


  // =========================================================
  // CHECK PRICE
  // =========================================================

  hasNoAmount(
    quote: ReceivedQuote
  ): boolean {

    return (

      quote.quoted_amount === null ||

      quote.quoted_amount === undefined ||

      quote.quoted_amount <= 0

    );

  }


  // =========================================================
  // STATUS COLOR
  // =========================================================

  statusColor(
    status: string
  ): string {

    switch (
      status?.toLowerCase()
    ) {

      case 'pending':

        return '#b7791f';


      case 'accepted':

        return '#15803d';


      case 'declined':

        return '#dc2626';


      case 'cancelled':

        return '#6b7280';


      case 'completed':

        return '#2563eb';


      default:

        return '#6b7280';

    }

  }


  // =========================================================
  // FORMAT DATE
  // =========================================================

  formatDate(
    date?: string
  ): string {

    if (!date) {

      return '';

    }


    return new Date(date)
      .toLocaleDateString(
        'en-IN',
        {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        }
      );

  }

}
