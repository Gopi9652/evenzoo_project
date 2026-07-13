import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PhotosManageComponent } from './photos-manage.component';

describe('PhotosManageComponent', () => {
  let component: PhotosManageComponent;
  let fixture: ComponentFixture<PhotosManageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PhotosManageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PhotosManageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
