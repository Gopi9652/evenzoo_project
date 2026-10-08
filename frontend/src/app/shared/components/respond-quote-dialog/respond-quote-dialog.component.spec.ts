import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RespondQuoteDialogComponent } from './respond-quote-dialog.component';

describe('RespondQuoteDialogComponent', () => {
  let component: RespondQuoteDialogComponent;
  let fixture: ComponentFixture<RespondQuoteDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RespondQuoteDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RespondQuoteDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
