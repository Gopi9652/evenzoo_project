import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Subscription } from 'rxjs';
import { MessageService } from '../../../core/services/message.service';
import { WebsocketService } from '../../../core/services/websocket.service';
import { NavbarComponent } from '../navbar/navbar.component';

@Component({
  selector: 'app-conversations-list',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatProgressSpinnerModule, NavbarComponent],
  templateUrl: './conversations-list.component.html',
  styleUrl: './conversations-list.component.scss'
})
export class ConversationsListComponent implements OnInit, OnDestroy {
  conversations: any[] = [];
  loading = true;
  private wsSubscription?: Subscription;

  constructor(
    private messageService: MessageService,
    private router: Router,
    private ws: WebsocketService
  ) {}

  ngOnInit() {
    this.loadConversations();

    this.wsSubscription = this.ws.onMessage().subscribe((msg) => {
      if (msg.type === 'chat_message') {
        // Simplest reliable fix: just reload the summary list from the server
        this.loadConversations();
      }
    });
  }

  ngOnDestroy() {
    this.wsSubscription?.unsubscribe();
  }

  loadConversations() {
    this.messageService.getConversations().subscribe({
      next: (data) => {
        this.conversations = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  openChat(conversation: any) {
    if (conversation.booking_id) {
      this.router.navigate(['/chat/booking', conversation.booking_id], {
        queryParams: { receiverId: conversation.other_user_id, name: conversation.other_user_name }
      });
    } else {
      this.router.navigate(['/chat/user', conversation.other_user_id], {
        queryParams: { name: conversation.other_user_name }
      });
    }
  }
}