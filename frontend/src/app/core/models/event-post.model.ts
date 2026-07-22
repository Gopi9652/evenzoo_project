export interface EventPost {
  id: number;
  customer_id: number;
  customer_name?: string;
  title: string;
  description: string;
  event_location: string;
  state_id?: number;
  city_id?: number;
  budget_amount?: number;
  event_date?: string;
  is_active: boolean;
  created_at: string;
}

export interface EventPostCreateRequest {
  title: string;
  description: string;
  event_location: string;
  state_id?: number;
  city_id?: number;
  budget_amount?: number;
  event_date?: string;
}