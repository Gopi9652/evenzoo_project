import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CinematicSceneComponent } from './cinematic-scene.component';

describe('CinematicSceneComponent', () => {
  let component: CinematicSceneComponent;
  let fixture: ComponentFixture<CinematicSceneComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CinematicSceneComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CinematicSceneComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
