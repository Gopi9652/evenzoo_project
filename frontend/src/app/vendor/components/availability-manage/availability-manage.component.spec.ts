import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AvailabilityManageComponent } from './availability-manage.component';

describe('AvailabilityManageComponent', () => {
  let component: AvailabilityManageComponent;
  let fixture: ComponentFixture<AvailabilityManageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AvailabilityManageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AvailabilityManageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
