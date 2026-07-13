export interface User {
  id: number;
  name: string;
  email: string;
  phone: string;
  role: 'customer' | 'vendor' | 'admin';
  is_verified: boolean;
  profile_photo?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  role: string;
  user_id: number;
  name: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  phone: string;
  password: string;
  role: 'customer' | 'vendor';
}

export interface LoginRequest {
  email: string;
  password: string;
}