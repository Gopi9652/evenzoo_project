import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SessionsManageComponent } from './sessions-manage.component';

describe('SessionsManageComponent', () => {
  let component: SessionsManageComponent;
  let fixture: ComponentFixture<SessionsManageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SessionsManageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SessionsManageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
