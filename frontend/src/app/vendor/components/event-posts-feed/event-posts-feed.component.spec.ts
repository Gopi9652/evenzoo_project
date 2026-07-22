import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EventPostsFeedComponent } from './event-posts-feed.component';

describe('EventPostsFeedComponent', () => {
  let component: EventPostsFeedComponent;
  let fixture: ComponentFixture<EventPostsFeedComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EventPostsFeedComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EventPostsFeedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
