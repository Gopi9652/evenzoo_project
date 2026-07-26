export interface VendorProfile {
  id: number;
  user_id: number;
  business_name: string;
  description?: string;
  city_id?: number;
  address?: string;
  is_approved: boolean;
  avg_rating?: number;
  total_reviews: number;
  total_bookings: number;
  profile_photo_url?: string;
}

export interface VendorService {
  id: number;
  vendor_id: number;
  name: string;
  description?: string;
  price: number;
  price_type: string;
  is_active: boolean;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
  icon?: string;
}