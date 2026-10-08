export interface EventPost {
  id: number;
  customer_id: number;
  customer_name?: string;
  title: string;
  description: string;
  event_location: string;
  state_id?: number;
  city_id?: number;
  category_id?: number;
  category_name?: string;
  budget_amount?: number;
  event_date?: string;
  is_active: boolean;
  created_at: string;
    // New fields
  items?: EventPostItem[];
  quote_count: number;
  allow_messages?: boolean;
  latitude?:any;
  longitude?:any;
  place_id?:any;
}

interface EventPostItem {
  id: number;
  category_name: string;
  budget_amount?: number | null;
  category_id?:any;
}
export interface EventPostCreateRequest {
  title: string;
  description: string;
  event_location: string;
  state_id?: number;
  city_id?: number;
  category_id?: number;
  budget_amount?: number;
  event_date?: string;
}