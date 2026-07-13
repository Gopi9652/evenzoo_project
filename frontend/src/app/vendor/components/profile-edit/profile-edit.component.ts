import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, FormsModule} from '@angular/forms';
import { VendorService } from '../../../core/services/vendor.service';
import { LocationService, City ,  State} from '../../../core/services/location.service';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { Category } from '../../../core/models/vendor.model';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';



@Component({
  selector: 'app-profile-edit',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, NavbarComponent, MatFormFieldModule,MatSelectModule,MatButtonModule,MatInputModule,FormsModule],
  templateUrl: './profile-edit.component.html',
  styleUrl: './profile-edit.component.scss'
})
export class ProfileEditComponent implements OnInit {
  profileForm: FormGroup;
  cities: City[] = [];
  states: State[] = [];
  allCategories: Category[] = [];
  myCategoryIds: Set<number> = new Set();
  loading = true;
  saving = false;
  savingCategory: number | null = null;
  successMessage = '';
  errorMessage = '';
selectedStateId: number | null = null;

  constructor(
    private fb: FormBuilder,
    private vendorService: VendorService,
    private locationService: LocationService
  ) {
    this.profileForm = this.fb.group({
      business_name: ['', Validators.required],
      description: [''],
      city_id: [''],
      address: [''],
      gstin: [''],
      pan_number: [''],
      bank_account: [''],
      bank_ifsc: [''],
      bank_name: ['']
    });
  }

    ngOnInit() {
    this.locationService.getStates().subscribe({
      next: (data) => this.states = data
    });
    
    this.vendorService.getCategories().subscribe({
      next: (data) => this.allCategories = data
    });
    this.vendorService.getMyProfile().subscribe({
      next: (data: any) => {
        this.profileForm.patchValue(data);
        this.loading = false;

        // If vendor already has a city set, figure out which state it belongs to
        // so the state dropdown pre-selects correctly and cities load for it
        if (data.city_id) {
          this.locationService.getCityById(data.city_id).subscribe({
            next: (city) => {
              this.selectedStateId = city.state_id;
              this.loadCitiesForState(city.state_id);
            }
          });
        }
      },
      error: () => this.loading = false
    });

    this.loadMyCategories()
  }

  loadCitiesForState(stateId: number) {
    this.locationService.getCities(stateId).subscribe({
      next: (data) => this.cities = data
    });
  }
  onStateChange() {
    this.profileForm.patchValue({ city_id: '' });  // reset city since it may not belong to new state
    if (this.selectedStateId) {
      this.loadCitiesForState(this.selectedStateId);
    } else {
      this.cities = [];
    }
  }

  loadMyCategories() {
    this.vendorService.getMyCategories().subscribe({
      next: (data) => {
        this.myCategoryIds = new Set(data.map(c => c.id));
      }
    });
  }

    isSelected(categoryId: number): boolean {
    return this.myCategoryIds.has(categoryId);
  }

  toggleCategory(categoryId: number) {
  if (this.savingCategory) return;
  this.savingCategory = categoryId;
    console.log(this.isSelected(categoryId))
  if (this.isSelected(categoryId)) {
    // Already selected → clicking removes it
    this.vendorService.removeCategory(categoryId).subscribe({
      next: () => {
         console.log(this.isSelected(categoryId))
        this.myCategoryIds.delete(categoryId);
        this.savingCategory = null;
      },
      error: () => this.savingCategory = null
    });
  } else {
    // Not selected → clicking adds it
    this.vendorService.assignCategory(categoryId).subscribe({
      next: () => {
        this.myCategoryIds.add(categoryId);
        this.savingCategory = null;
      },
      error: () => this.savingCategory = null
    });
  }
}

onSubmit() {
    if (this.profileForm.invalid) {
      this.profileForm.markAllAsTouched();
      return;
    }

    this.saving = true;
    this.successMessage = '';
    this.errorMessage = '';

    this.vendorService.updateMyProfile(this.profileForm.value).subscribe({
      next: () => {
        this.saving = false;
        this.successMessage = 'Profile updated successfully!';
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (err) => {
        this.saving = false;
        this.errorMessage = err.error?.detail || 'Failed to update profile';
      }
    });
  }
}