import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ApprovalBannerComponent } from './approval-banner.component';

describe('ApprovalBannerComponent', () => {
  let component: ApprovalBannerComponent;
  let fixture: ComponentFixture<ApprovalBannerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ApprovalBannerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ApprovalBannerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
