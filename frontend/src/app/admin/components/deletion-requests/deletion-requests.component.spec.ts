import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeletionRequestsComponent } from './deletion-requests.component';

describe('DeletionRequestsComponent', () => {
  let component: DeletionRequestsComponent;
  let fixture: ComponentFixture<DeletionRequestsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DeletionRequestsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DeletionRequestsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
