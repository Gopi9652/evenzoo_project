

export interface BookingCreateRequest {
  vendor_id: number;
  event_type_id: number;
  event_date: string;
  event_time?: string;
  event_location: string;
  guests_count?: number;
  special_requests?: string;
  service_ids: number[];
}

export interface BookedServiceItem {
  service_id: number;
  name: string;
  quantity: number;
  unit_price: number;
  total: number;
}

export interface Booking {
  id: number;
  booking_ref: string;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  event_date: string;
  event_time?: string;
  event_location: string;
  guests_count?: number;
  special_requests?: string;
  total_amount: number;
  platform_fee?: number;
  vendor_amount?: number;
  event_type_name?: string;
  created_at: string;
  cancellation_reason?: string;

  customer_id: number;
  customer_name: string;
  customer_phone?: string;
  customer_email?: string;
  vendor_id: number;
  vendor_user_id: number;
  vendor_business_name: string;
  vendor_phone?: string;

  services: BookedServiceItem[];
}