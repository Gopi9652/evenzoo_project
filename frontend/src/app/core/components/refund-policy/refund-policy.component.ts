import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-refund-policy',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './refund-policy.component.html',
  styleUrl: './refund-policy.component.scss'
})
export class RefundPolicyComponent {
  lastUpdated = 'July 15, 2026';
}