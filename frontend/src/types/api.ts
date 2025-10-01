export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  parent_id?: string;
  path: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  children?: Category[];
}

export interface Product {
  id: string;
  name: string;
  description: string;
  category_id: string;
  seller_id: string;
  seller_price: number;
  commission_rate: number;
  commission_amount: number;
  customer_price: number;
  stock_quantity: number;
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'archived';
  tags: string;
  weight?: number;
  dimensions?: string;
  meta_title?: string;
  meta_description?: string;
  admin_notes?: string;
  created_at: string;
  updated_at: string;
  category: Category;
  seller: Seller;
  images: ProductImage[];
  variants: ProductVariant[];
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
  product_id: string;
  sku: string;
  seller_price: number;
  commission_rate: number;
  commission_amount: number;
  customer_price: number;
  stock_quantity: number;
  weight?: number;
  dimensions?: string;
  is_active: boolean;
}

export interface Order {
  id: string;
  customer_id: string;
  total_amount: number;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  payment_status: 'cod_pending' | 'cod_collected' | 'paid' | 'refunded';
  delivery_address: string;
  delivery_city: string;
  delivery_state: string;
  delivery_pincode: string;
  phone: string;
  notes?: string;
  admin_notes?: string;
  created_at: string;
  updated_at: string;
  customer: User;
  items: OrderItem[];
}

export interface OrderItem {
  id: string;
  order_id: string;
  product_id: string;
  product_variant_id?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  product: Product;
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
  total_sellers: number;
  total_customers: number;
  active_users: number;
  verified_sellers: number;
  pending_seller_verification: number;
}

export interface OrderStats {
  total_orders: number;
  pending_orders: number;
  processing_orders: number;
  shipped_orders: number;
  delivered_orders: number;
  cancelled_orders: number;
  total_revenue: number;
  pending_payment: number;
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