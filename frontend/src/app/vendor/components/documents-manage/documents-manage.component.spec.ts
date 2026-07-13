import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DocumentsManageComponent } from './documents-manage.component';

describe('DocumentsManageComponent', () => {
  let component: DocumentsManageComponent;
  let fixture: ComponentFixture<DocumentsManageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DocumentsManageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DocumentsManageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
