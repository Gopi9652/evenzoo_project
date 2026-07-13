import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorApprovalsComponent } from './vendor-approvals.component';

describe('VendorApprovalsComponent', () => {
  let component: VendorApprovalsComponent;
  let fixture: ComponentFixture<VendorApprovalsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorApprovalsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VendorApprovalsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
