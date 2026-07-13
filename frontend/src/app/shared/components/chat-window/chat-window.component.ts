import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Subscription } from 'rxjs';
import { MessageService } from '../../../core/services/message.service';
import { WebsocketService } from '../../../core/services/websocket.service';
import { NavbarComponent } from '../navbar/navbar.component';

@Component({
  selector: 'app-chat-window',
  standalone: true,
  imports: [CommonModule, FormsModule, MatIconModule, MatButtonModule, MatProgressSpinnerModule, NavbarComponent],
  templateUrl: './chat-window.component.html',
  styleUrl: './chat-window.component.scss'
})
export class ChatWindowComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('messagesEnd') messagesEnd!: ElementRef;

  mode: 'booking' | 'user' = 'user';
  bookingId: number | null = null;
  receiverId!: number;   // known immediately from the route — never depends on message history
  otherPartyName = '';

  messages: any[] = [];
  newMessage = '';
  loading = true;
  currentUserId!: number;
  private wsSubscription?: Subscription;

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private messageService: MessageService,
    private ws: WebsocketService
  ) {}

  ngOnInit() {
    this.currentUserId = Number(localStorage.getItem('user_id'));

    // Route can be either /chat/booking/:bookingId?receiverId=X&name=Y
    // or /chat/user/:userId?name=Y
    const bookingIdParam = this.route.snapshot.paramMap.get('bookingId');
    const userIdParam = this.route.snapshot.paramMap.get('userId');

    this.route.queryParams.subscribe(params => {
      this.otherPartyName = params['name'] || 'Chat';

      if (bookingIdParam) {
        this.mode = 'booking';
        this.bookingId = Number(bookingIdParam);
        this.receiverId = Number(params['receiverId']);
        this.loadBookingConversation();
      } else if (userIdParam) {
        this.mode = 'user';
        this.receiverId = Number(userIdParam);
        this.loadDirectConversation();
      }
    });

    this.wsSubscription = this.ws.onMessage().subscribe((msg) => {
      if (msg.type !== 'chat_message') return;

      const isRelevant = this.mode === 'booking'
        ? msg.data.booking_id === this.bookingId
        : (!msg.data.booking_id &&
          ((msg.data.sender_id === this.receiverId && msg.data.receiver_id === this.currentUserId) ||
            (msg.data.sender_id === this.currentUserId && msg.data.receiver_id === this.receiverId)));

      if (isRelevant) {
        this.messages = [...this.messages, msg.data];  // new array reference instead of .push()
      }
    });
  }

  ngOnDestroy() {
    this.wsSubscription?.unsubscribe();
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  loadBookingConversation() {
    this.loading = true;
    this.messageService.getConversationByBooking(this.bookingId!).subscribe({
      next: (data) => {
        this.messages = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  loadDirectConversation() {
    this.loading = true;
    this.messageService.getConversationDirect(this.receiverId).subscribe({
      next: (data) => {
        this.messages = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  send() {
    if (!this.newMessage.trim() || !this.receiverId) return;

    const content = this.newMessage.trim();
    this.messageService.sendMessage(
      this.receiverId,
      content,
      this.mode === 'booking' ? this.bookingId! : undefined
    ).subscribe({
      next: (msg) => {
        this.messages = [...this.messages, msg];  // new array reference here too
        this.newMessage = '';
      },
      error: (err) => alert(err.error?.detail || 'Failed to send message')
    });
  }

  scrollToBottom() {
    try {
      this.messagesEnd?.nativeElement.scrollIntoView({ behavior: 'smooth' });
    } catch {}
  }

  isMine(msg: any): boolean {
    return msg.sender_id === this.currentUserId;
  }
}