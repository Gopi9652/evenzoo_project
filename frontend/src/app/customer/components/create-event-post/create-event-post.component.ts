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
@Component({
  selector: 'app-create-event-post',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatFormFieldModule, MatInputModule,
    MatSelectModule, MatButtonModule, MatDatepickerModule, MatNativeDateModule,
    NavbarComponent, FormsModule
  ],
  templateUrl: './create-event-post.component.html',
  styleUrl: './create-event-post.component.scss'
})
export class CreateEventPostComponent implements OnInit {
  postForm: FormGroup;
  states: State[] = [];
  cities: City[] = [];
  categories: Category[] = [];
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
      event_date: ['']
    });
  }

  ngOnInit() {
    this.locationService.getStates().subscribe({
      next: (data) => this.states = data
    });

    this.vendorService.getCategories().subscribe({    // ← new
      next: (data) => this.categories = data
    });

    // Support editing an existing post via query param, e.g. /customer/post/create?edit=5
    const editId = this.route.snapshot.queryParamMap.get('edit');
    if (editId) {
      this.editMode = true;
      this.editPostId = Number(editId);
      this.eventPostService.getPostById(this.editPostId).subscribe({
        next: (post) => {
          this.postForm.patchValue(post);
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
}