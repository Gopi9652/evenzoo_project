import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateEventPostComponent } from './create-event-post.component';

describe('CreateEventPostComponent', () => {
  let component: CreateEventPostComponent;
  let fixture: ComponentFixture<CreateEventPostComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateEventPostComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateEventPostComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
