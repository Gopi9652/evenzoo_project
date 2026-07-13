export interface Booking {
  id: number;
  booking_ref: string;
  customer_id: number;
  vendor_id: number;
  event_type_id?: number;
  event_date: string;
  event_time?: string;
  event_location: string;
  guests_count?: number;
  special_requests?: string;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  total_amount: number;
  platform_fee?: number;
  vendor_amount?: number;
  created_at: string;
}

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