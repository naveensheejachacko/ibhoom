export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  icon_url?: string;
  parent_id?: string;
  path: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  children?: Category[];
}

export interface SellerBasicInfo {
  id: string;
  business_name: string;
  business_type?: string;
  city?: string;
  state?: string;
  pincode?: string;
  email?: string;
  phone?: string;
}

export interface Product {
  id: string;
  name: string;
  slug?: string;
  description: string;
  short_description?: string;
  category_id: string;
  seller_id: string;
  // For list responses
  seller_price?: number;
  commission_rate?: number;
  commission_amount?: number;
  sku?: string;
  // For detail responses
  customer_price: number;
  tax_rate?: number;
  tax_amount?: number;
  final_unit_price?: number;
  stock_quantity: number;
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'blocked' | 'archived';
  tags: string;
  weight?: number;
  dimensions?: string;
  meta_title?: string;
  meta_description?: string;
  admin_notes?: string;
  // Return Policy fields
  has_return_policy?: boolean;
  return_period_days?: number;
  return_policy_description?: string;
  // Newly Arrived (Admin only)
  is_newly_arrived?: boolean;
  created_at: string;
  updated_at: string;
  category?: Category;
  seller?: SellerBasicInfo;  // Seller basic details
  images: ProductImage[];
  variants: ProductVariant[];
  reviews?: any[];
  seller_name?: string;
  seller_email?: string;
  average_rating?: number;
  total_reviews?: number;
}

export interface ProductImage {
  id: string;
  product_id: string;
  image_url: string;
  alt_text?: string;
  sort_order: number;
}

export interface ProductVariant {
  id: string;
  product_id?: string;
  variant_name?: string;
  sku: string;
  seller_price?: number;
  commission_rate?: number;
  commission_amount?: number;
  customer_price: number;
  tax_rate?: number;
  tax_amount?: number;
  final_unit_price?: number;
  stock_quantity: number;
  weight?: number;
  dimensions?: string;
  is_active: boolean;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface Order {
  id: string;
  order_number: string;
  customer_id: string;
  total_customer_amount: number;
  total_seller_amount: number;
  total_commission_amount: number;
  status: 'PENDING' | 'REJECTED' | 'PROCESSING' | 'READY_FOR_DISPATCH' | 'DISPATCHED' | 'DELIVERED' | 'CANCELLED' | 'RETURN_REQUESTED' | 'RETURN_APPROVED' | 'RETURN_REJECTED' | 'RETURN_PICKED_UP' | 'RETURN_RECEIVED' | 'REFUND_PROCESSING' | 'REFUND_COMPLETED';
  payment_status: 'cod_pending' | 'cod_collected' | 'paid' | 'refunded';
  delivery_address: string;
  delivery_city: string;
  delivery_state: string;
  delivery_pincode: string;
  phone: string;
  notes?: string;
  admin_notes?: string;
  seller_notes?: string;
  return_reason?: string;
  return_notes?: string;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

export interface OrderListResponse {
  id: string;
  order_number: string;
  customer_id: string;
  customer_name?: string;
  total_customer_amount: number;
  total_tax_amount?: number;
  grand_total_amount?: number;
  payable_amount?: number;  // Amount payable to seller
  commission_amount?: number;  // Total commission admin gets for this order
  delivery_address?: string;
  delivery_city?: string;
  delivery_state?: string;
  delivery_pincode?: string;
  phone?: string;
  total_items: number;
  status: string;
  payment_status: string;
  created_at: string;
  items: OrderListItem[];
  return_reason?: string;
  return_requested_at?: string;
  refund_amount?: number;
  refund_date?: string;
  refund_notes?: string;
}

export interface OrderListItem {
  id: string;
  product_id: string;
  product_variant_id?: string;
  product_name: string;
  variant_name?: string;
  product_image?: string;
  seller_name?: string;
  quantity: number;
  customer_unit_price: number;
  total_customer_amount: number;
}

export interface OrderItem {
  id: string;
  product_id: string;
  product_variant_id?: string;
  quantity: number;
  seller_unit_price: number;
  customer_unit_price: number;
  commission_unit_rate: number;
  commission_unit_amount: number;
  total_seller_amount: number;
  total_customer_amount: number;
  total_commission_amount: number;
  product_name: string;
  variant_name?: string;
  product_image?: string;
}

export interface Commission {
  id: string;
  type: 'global' | 'category' | 'product';
  entity_id?: string;
  commission_rate: number;
  min_seller_price: number;
  max_seller_price?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Statistics {
  total_users: number;
  active_users: number;
  verified_users: number;
  total_sellers: number;
  active_sellers: number;
  verified_sellers: number;
  total_customers: number;
  active_customers: number;
}

export interface OrderStats {
  total_orders: number;
  pending_orders: number;
  processing_orders: number;
  shipped_orders: number;
  delivered_orders: number;
  cancelled_orders: number;
  total_revenue: number;
  total_commission: number;
}

export interface Seller {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  business_name: string;
  business_type: string;
  address: string;
  city: string;
  state: string;
  pincode: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
} 