import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { EventPostService } from '../../../core/services/event-post.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { EventPost } from '../../../core/models/event-post.model';

@Component({
  selector: 'app-my-event-posts',
  standalone: true,
  imports: [CommonModule, RouterLink, MatButtonModule, MatIconModule, MatProgressSpinnerModule, NavbarComponent],
  templateUrl: './my-event-posts.component.html',
  styleUrl: './my-event-posts.component.scss'
})
export class MyEventPostsComponent implements OnInit {
  posts: EventPost[] = [];
  loading = true;

  constructor(
    private eventPostService: EventPostService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadPosts();
  }

  loadPosts() {
    this.loading = true;
    this.eventPostService.getMyPosts().subscribe({
      next: (data) => {
        this.posts = data;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  editPost(postId: number) {
    this.router.navigate(['/customer/post/create'], { queryParams: { edit: postId } });
  }

  deletePost(postId: number) {
    if (!confirm('Delete this event post? Vendors will no longer be able to see or message you about it.')) return;

    this.eventPostService.deletePost(postId).subscribe({
      next: () => this.loadPosts(),
      error: (err) => alert(err.error?.detail || 'Failed to delete post')
    });
  }
}