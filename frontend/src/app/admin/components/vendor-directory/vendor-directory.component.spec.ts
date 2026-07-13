import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorDirectoryComponent } from './vendor-directory.component';

describe('VendorDirectoryComponent', () => {
  let component: VendorDirectoryComponent;
  let fixture: ComponentFixture<VendorDirectoryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorDirectoryComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VendorDirectoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
