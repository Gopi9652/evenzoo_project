import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyEventPostsComponent } from './my-event-posts.component';

describe('MyEventPostsComponent', () => {
  let component: MyEventPostsComponent;
  let fixture: ComponentFixture<MyEventPostsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MyEventPostsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MyEventPostsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
