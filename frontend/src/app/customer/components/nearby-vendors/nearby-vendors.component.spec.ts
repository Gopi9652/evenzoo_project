import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NearbyVendorsComponent } from './nearby-vendors.component';

describe('NearbyVendorsComponent', () => {
  let component: NearbyVendorsComponent;
  let fixture: ComponentFixture<NearbyVendorsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NearbyVendorsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NearbyVendorsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
