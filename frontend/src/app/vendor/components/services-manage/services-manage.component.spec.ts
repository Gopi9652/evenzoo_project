import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ServicesManageComponent } from './services-manage.component';

describe('ServicesManageComponent', () => {
  let component: ServicesManageComponent;
  let fixture: ComponentFixture<ServicesManageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ServicesManageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ServicesManageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
