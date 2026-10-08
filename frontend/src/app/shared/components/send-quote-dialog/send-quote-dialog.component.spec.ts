import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SendQuoteDialogComponent } from './send-quote-dialog.component';

describe('SendQuoteDialogComponent', () => {
  let component: SendQuoteDialogComponent;
  let fixture: ComponentFixture<SendQuoteDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SendQuoteDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SendQuoteDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
