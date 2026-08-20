import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorCompareComponent } from './vendor-compare.component';

describe('VendorCompareComponent', () => {
  let component: VendorCompareComponent;
  let fixture: ComponentFixture<VendorCompareComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorCompareComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VendorCompareComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
