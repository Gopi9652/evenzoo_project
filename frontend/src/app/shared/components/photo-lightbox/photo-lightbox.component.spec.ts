import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PhotoLightboxComponent } from './photo-lightbox.component';

describe('PhotoLightboxComponent', () => {
  let component: PhotoLightboxComponent;
  let fixture: ComponentFixture<PhotoLightboxComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PhotoLightboxComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PhotoLightboxComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
