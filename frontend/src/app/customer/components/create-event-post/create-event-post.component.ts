import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { EventPostService } from '../../../core/services/event-post.service';
import { LocationService, State, City } from '../../../core/services/location.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { VendorService } from '../../../core/services/vendor.service';
import { Category } from '../../../core/models/vendor.model';

import { FormArray } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { LocationPickerComponent, PickedLocation } from '../../../shared/components/location-picker/location-picker.component';

@Component({
  selector: 'app-create-event-post',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatFormFieldModule, MatInputModule,
    MatSelectModule, MatButtonModule, MatDatepickerModule, MatNativeDateModule,
    NavbarComponent, FormsModule, MatIconModule, MatCheckboxModule, LocationPickerComponent
  ],
  templateUrl: './create-event-post.component.html',
  styleUrl: './create-event-post.component.scss'
})
export class CreateEventPostComponent implements OnInit {
  postForm: FormGroup;
  categories: Category[] = [];
  states: State[] = [];
  cities: City[] = [];
  selectedStateId: number | null = null;
  submitting = false;
  errorMessage = '';
  editMode = false;
  editPostId: number | null = null;
  minDate = new Date();

  constructor(
    private fb: FormBuilder,
    private eventPostService: EventPostService,
    private locationService: LocationService,
    private router: Router,
    private route: ActivatedRoute,
    private vendorService: VendorService,
  ) {
    this.postForm = this.fb.group({
      title: ['', [Validators.required, Validators.minLength(5)]],
      description: ['', [Validators.required, Validators.minLength(20)]],
      event_location: ['', Validators.required],
      city_id: [''],
      category_id: [''], 
      budget_amount: [''],
      event_date: [''],
      allow_messages: [true],
      response_deadline: [''],
      items: this.fb.array([this.createItemGroup()])  
    });
  }

  ngOnInit() {
    this.locationService.getStates().subscribe({ next: (data) => this.states = data });
    this.vendorService.getCategories().subscribe({ next: (data) => this.categories = data });

    const editId = this.route.snapshot.queryParamMap.get('edit');
    if (editId) {
      this.editMode = true;
      this.editPostId = Number(editId);
      this.eventPostService.getPostById(this.editPostId).subscribe({
        next: (post) => {
          // Patch the plain fields normally
          this.postForm.patchValue({
            title: post.title,
            description: post.description,
            event_location: post.event_location,
            city_id: post.city_id,
            event_date: post.event_date,
            allow_messages: post.allow_messages,
            latitude: post.latitude,
            longitude: post.longitude,
            place_id: post.place_id
          });

          // Rebuild the items FormArray to match what was actually saved —
          // patchValue cannot populate a FormArray from a plain data array
          this.items.clear();
          if (post.items && post.items.length > 0) {
            post.items.forEach((item: any) => {
              this.items.push(this.fb.group({
                category_id: [item.category_id, Validators.required],
                budget_amount: [item.budget_amount]
              }));
            });
          } else if (post.category_id) {
            // Backward compatibility: an older post saved with only the single category_id field
            this.items.push(this.fb.group({
              category_id: [post.category_id, Validators.required],
              budget_amount: [post.budget_amount]
            }));
          } else {
            this.items.push(this.createItemGroup());
          }

          if (post.city_id) {
            this.locationService.getCityById(post.city_id).subscribe({
              next: (city) => {
                this.selectedStateId = city.state_id;
                this.loadCities(city.state_id);
              }
            });
          }
        }
      });
    }
  }

  onStateChange() {
    this.postForm.patchValue({ city_id: '' });
    if (this.selectedStateId) {
      this.loadCities(this.selectedStateId);
    } else {
      this.cities = [];
    }
  }

  loadCities(stateId: number) {
    this.locationService.getCities(stateId).subscribe({
      next: (data) => this.cities = data
    });
  }
   get items(): FormArray {
    return this.postForm.get('items') as FormArray;
  }

  createItemGroup(): FormGroup {
    return this.fb.group({
      category_id: ['', Validators.required],
      budget_amount: ['']
    });
  }

  addEventItem() {
    this.items.push(this.createItemGroup());
  }

  removeEventItem(index: number) {
    if (this.items.length > 1) this.items.removeAt(index);
  }

  onSubmit() {
  if (this.postForm.invalid) {
    this.postForm.markAllAsTouched();
    return;
  }

  this.submitting = true;
  this.errorMessage = '';

  const formValue = { ...this.postForm.value, state_id: this.selectedStateId };
  if (formValue.event_date instanceof Date) {
    formValue.event_date = formValue.event_date.toISOString();
  }
  if (formValue.response_deadline instanceof Date) {
    formValue.response_deadline = formValue.response_deadline.toISOString();
  }

  if (formValue.items.length > 0) {
    formValue.category_id = formValue.items[0].category_id;
    formValue.budget_amount = formValue.items[0].budget_amount;
  }

  const request$ = this.editMode
    ? this.eventPostService.updatePost(this.editPostId!, formValue)
    : this.eventPostService.createPost(formValue);

  request$.subscribe({
    next: () => {
      this.submitting = false;
      this.router.navigate(['/customer/my-posts']);
    },
    error: (err) => {
      this.submitting = false;
      this.errorMessage = err.error?.detail || 'Failed to save post';
    }
  });
}
  onLocationPicked(loc: PickedLocation) {
    this.postForm.patchValue({
      latitude: loc.latitude,
      longitude: loc.longitude,
      place_id: loc.place_id
    });
  }
}