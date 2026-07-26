import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WorkingHoursManageComponent } from './working-hours-manage.component';

describe('WorkingHoursManageComponent', () => {
  let component: WorkingHoursManageComponent;
  let fixture: ComponentFixture<WorkingHoursManageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WorkingHoursManageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(WorkingHoursManageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
