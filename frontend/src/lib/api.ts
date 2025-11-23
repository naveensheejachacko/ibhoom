import axios from 'axios';
import type { LoginRequest, LoginResponse } from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for automatic token refresh
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (error?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');

      if (!refreshToken) {
        // No refresh token, logout user
        processQueue(new Error('No refresh token'), null);
        isRefreshing = false;
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        // Make direct API call to refresh endpoint (bypass interceptor to avoid circular dependency)
        const refreshResponse = await axios.post(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken },
          { headers: { 'Content-Type': 'application/json' } }
        );
        
        const { access_token, refresh_token: new_refresh_token } = refreshResponse.data;
        
        // Update tokens in localStorage
        localStorage.setItem('token', access_token);
        localStorage.setItem('refresh_token', new_refresh_token);
        
        // Update the original request with new token
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        
        // Process queued requests
        processQueue(null, access_token);
        isRefreshing = false;
        
        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        processQueue(refreshError, null);
        isRefreshing = false;
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post('/api/v1/auth/login', {
      email: credentials.email,
      password: credentials.password,
    });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/api/v1/auth/me');
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<LoginResponse> => {
    const response = await api.post('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  registerSeller: async (data: any) => {
    const response = await api.post('/api/v1/auth/register/seller', data);
    return response.data;
  },

  registerAdmin: async (data: any) => {
    const response = await api.post('/api/v1/auth/register/admin', data);
    return response.data;
  },
};

// Admin API
export const adminApi = {
  // Statistics
  getUserStats: async () => {
    const response = await api.get('/api/v1/admin/users/stats');
    return response.data;
  },
  
  getOrderStats: async () => {
    const response = await api.get('/api/v1/admin/orders/stats');
    return response.data;
  },
  
  // Categories
  getCategories: async () => {
    const response = await api.get('/api/v1/admin/categories');
    return response.data;
  },
  
  getCategoryTree: async () => {
    const response = await api.get('/api/v1/admin/categories/tree');
    return response.data;
  },
  
  createCategory: async (data: any, iconFile?: File) => {
    const formData = new FormData();
    formData.append('name', data.name);
    if (data.description) formData.append('description', data.description);
    if (data.parent_id) formData.append('parent_id', data.parent_id);
    if (data.sort_order !== undefined) formData.append('sort_order', data.sort_order.toString());
    if (data.is_active !== undefined) formData.append('is_active', data.is_active.toString());
    if (iconFile) {
      formData.append('icon', iconFile);
    } else if (data.icon_url) {
      formData.append('icon_url', data.icon_url);
    }
    const response = await api.post('/api/v1/admin/categories', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  updateCategory: async (id: string, data: any, iconFile?: File) => {
    const formData = new FormData();
    if (data.name !== undefined) formData.append('name', data.name);
    if (data.description !== undefined) formData.append('description', data.description || '');
    if (data.parent_id !== undefined) formData.append('parent_id', data.parent_id || '');
    if (data.sort_order !== undefined) formData.append('sort_order', data.sort_order.toString());
    if (data.is_active !== undefined) formData.append('is_active', data.is_active.toString());
    if (iconFile) {
      formData.append('icon', iconFile);
    } else if (data.icon_url !== undefined) {
      formData.append('icon_url', data.icon_url || '');
    }
    const response = await api.put(`/api/v1/admin/categories/${id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  deleteCategory: async (id: string) => {
    const response = await api.delete(`/api/v1/admin/categories/${id}`);
    return response.data;
  },
  
  // Products
  getProducts: async (params?: any) => {
    const response = await api.get('/api/v1/admin/products', { params });
    return response.data;
  },
  
  getPendingProducts: async (params?: any) => {
    const response = await api.get('/api/v1/admin/products/pending', { params });
    return response.data;
  },
  
  getProduct: async (id: string) => {
    const response = await api.get(`/api/v1/admin/products/${id}`);
    return response.data;
  },
  
  approveProduct: async (id: string, data: any) => {
    const response = await api.put(`/api/v1/admin/products/${id}/approve`, data);
    return response.data;
  },
  
  recalculateCommission: async (id: string) => {
    const response = await api.post(`/api/v1/admin/products/${id}/recalculate-commission`);
    return response.data;
  },
  
  deleteProduct: async (id: string) => {
    const response = await api.delete(`/api/v1/admin/products/${id}`);
    return response.data;
  },
  
  // Users
  getUsers: async (params?: any) => {
    const response = await api.get('/api/v1/admin/users', { params });
    return response.data;
  },
  
  getSellers: async (params?: any) => {
    const response = await api.get('/api/v1/admin/users/sellers', { params });
    return response.data;
  },
  
  updateSellerStatus: async (sellerId: string, data: any) => {
    const response = await api.put(`/api/v1/admin/users/sellers/${sellerId}/status`, data);
    return response.data;
  },
  
  updateUserStatus: async (id: string, data: any) => {
    const response = await api.put(`/api/v1/admin/users/${id}/status`, data);
    return response.data;
  },
  
  // Orders
  getOrders: async (params?: any) => {
    const response = await api.get('/api/v1/admin/orders', { params });
    return response.data;
  },
  
  getPendingOrders: async (params?: any) => {
    const response = await api.get('/api/v1/admin/orders/pending', { params });
    return response.data;
  },
  
  getOrder: async (id: string) => {
    const response = await api.get(`/api/v1/admin/orders/${id}`);
    return response.data;
  },
  
  updateOrderStatus: async (id: string, data: any) => {
    const response = await api.put(`/api/v1/admin/orders/${id}/status`, data);
    return response.data;
  },
  
  updatePaymentStatus: async (id: string, data: any) => {
    const response = await api.put(`/api/v1/admin/orders/${id}/payment`, data);
    return response.data;
  },
  
  cancelOrder: async (id: string, adminNotes?: string) => {
    const response = await api.post(`/api/v1/admin/orders/${id}/cancel`, null, {
      params: { admin_notes: adminNotes }
    });
    return response.data;
  },

  downloadInvoice: async (id: string) => {
    const response = await api.get(`/api/v1/admin/orders/${id}/invoice`, {
      responseType: 'blob',
    });
    return response.data;
  },
  
  // Commissions
  getCommissions: async () => {
    const response = await api.get('/api/v1/admin/commissions');
    return response.data;
  },
  
  createCommission: async (data: any) => {
    const response = await api.post('/api/v1/admin/commissions', data);
    return response.data;
  },
  
  updateCommission: async (id: string, data: any) => {
    const response = await api.put(`/api/v1/admin/commissions/${id}`, data);
    return response.data;
  },
  
  deleteCommission: async (id: string) => {
    const response = await api.delete(`/api/v1/admin/commissions/${id}`);
    return response.data;
  },

  // Attributes
  getAttributes: async () => {
    const response = await api.get('/api/v1/admin/attributes');
    return response.data;
  },

  getAttribute: async (id: string) => {
    const response = await api.get(`/api/v1/admin/attributes/${id}`);
    return response.data;
  },

  createAttribute: async (data: any) => {
    const response = await api.post('/api/v1/admin/attributes', data);
    return response.data;
  },

  updateAttribute: async (id: string, data: any) => {
    const response = await api.put(`/api/v1/admin/attributes/${id}`, data);
    return response.data;
  },

  deleteAttribute: async (id: string) => {
    const response = await api.delete(`/api/v1/admin/attributes/${id}`);
    return response.data;
  },

  // Attribute Values
  getAttributeValues: async (attributeId: string) => {
    const response = await api.get(`/api/v1/admin/attributes/${attributeId}/values`);
    return response.data;
  },

  createAttributeValue: async (data: any) => {
    const response = await api.post('/api/v1/admin/attributes/values', data);
    return response.data;
  },

  updateAttributeValue: async (id: string, data: any) => {
    const response = await api.put(`/api/v1/admin/attributes/values/${id}`, data);
    return response.data;
  },

  deleteAttributeValue: async (id: string) => {
    const response = await api.delete(`/api/v1/admin/attributes/values/${id}`);
    return response.data;
  },

  // Category Attributes
  getCategoryAttributes: async (categoryId: string) => {
    const response = await api.get(`/api/v1/admin/attributes/category-attributes/${categoryId}`);
    return response.data;
  },

  createCategoryAttribute: async (data: any) => {
    const response = await api.post('/api/v1/admin/attributes/category-attributes', data);
    return response.data;
  },

  updateCategoryAttribute: async (id: string, data: any) => {
    const response = await api.put(`/api/v1/admin/attributes/category-attributes/${id}`, data);
    return response.data;
  },

  deleteCategoryAttribute: async (id: string) => {
    const response = await api.delete(`/api/v1/admin/attributes/category-attributes/${id}`);
    return response.data;
  },

  // Notifications
  getNotifications: async (params?: { skip?: number; limit?: number; unread_only?: boolean }) => {
    const response = await api.get('/api/v1/admin/notifications', { params });
    return response.data;
  },

  getUnreadCount: async () => {
    const response = await api.get('/api/v1/admin/notifications/unread-count');
    return response.data;
  },

  markNotificationRead: async (notificationId: string) => {
    const response = await api.put(`/api/v1/admin/notifications/${notificationId}/read`);
    return response.data;
  },

  markAllNotificationsRead: async () => {
    const response = await api.put('/api/v1/admin/notifications/mark-all-read');
    return response.data;
  },

  // Banners
  getBanners: async (params?: any) => {
    const response = await api.get('/api/v1/admin/banners', { params });
    return response.data;
  },
  
  getBanner: async (id: string) => {
    const response = await api.get(`/api/v1/admin/banners/${id}`);
    return response.data;
  },
  
  createBanner: async (data: any, imageFile?: File) => {
    const formData = new FormData();
    formData.append('title', data.title);
    if (data.description) formData.append('description', data.description);
    if (data.link_url) formData.append('link_url', data.link_url);
    formData.append('position', data.position);
    formData.append('status', data.status);
    formData.append('sort_order', data.sort_order.toString());
    if (data.start_date) formData.append('start_date', data.start_date);
    if (data.end_date) formData.append('end_date', data.end_date);
    if (data.category_id) formData.append('category_id', data.category_id);
    if (data.product_id) formData.append('product_id', data.product_id);
    if (imageFile) {
      formData.append('image', imageFile);
    }
    const response = await api.post('/api/v1/admin/banners', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  updateBanner: async (id: string, data: any, imageFile?: File) => {
    const formData = new FormData();
    if (data.title !== undefined) formData.append('title', data.title);
    if (data.description !== undefined) formData.append('description', data.description || '');
    if (data.link_url !== undefined) formData.append('link_url', data.link_url || '');
    if (data.position !== undefined) formData.append('position', data.position);
    if (data.status !== undefined) formData.append('status', data.status);
    if (data.sort_order !== undefined) formData.append('sort_order', data.sort_order.toString());
    if (data.start_date !== undefined) formData.append('start_date', data.start_date || '');
    if (data.end_date !== undefined) formData.append('end_date', data.end_date || '');
    // Handle category_id and product_id - send empty string to clear, or value to set
    if (data.category_id !== undefined) formData.append('category_id', data.category_id || '');
    if (data.product_id !== undefined) formData.append('product_id', data.product_id || '');
    if (imageFile) {
      formData.append('image', imageFile);
    }
    const response = await api.put(`/api/v1/admin/banners/${id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  deleteBanner: async (id: string) => {
    const response = await api.delete(`/api/v1/admin/banners/${id}`);
    return response.data;
  },
};

// Seller API
export const sellerApi = {
  // Products
  getProducts: async (params?: any) => {
    const response = await api.get('/api/v1/seller/products', { params });
    return response.data;
  },
  
  getProduct: async (id: string) => {
    const response = await api.get(`/api/v1/seller/products/${id}/`);
    return response.data;
  },
  
  createProduct: async (data: any) => {
    const response = await api.post('/api/v1/seller/products/', data);
    return response.data;
  },
  
  updateProduct: async (id: string, data: any) => {
    const response = await api.put(`/api/v1/seller/products/${id}/`, data);
    return response.data;
  },
  
  deleteProduct: async (id: string) => {
    const response = await api.delete(`/api/v1/seller/products/${id}/`);
    return response.data;
  },
  
  getPendingCount: async () => {
    const response = await api.get('/api/v1/seller/products/pending/count');
    return response.data;
  },
  
  getApprovedCount: async () => {
    const response = await api.get('/api/v1/seller/products/approved/count');
    return response.data;
  },

  
  // Profile
  getProfile: async () => {
    const response = await api.get('/api/v1/seller/profile/');
    return response.data;
  },

  updateProfile: async (formData: FormData) => {
    const response = await api.put('/api/v1/seller/profile/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  updatePassword: async (data: { current_password: string; new_password: string }) => {
    const response = await api.put('/api/v1/seller/profile/password', data);
    return response.data;
  },

  // Orders
  getOrders: async (params?: any) => {
    const response = await api.get('/api/v1/seller/orders', { params });
    return response.data;
  },

  getOrder: async (id: string) => {
    const response = await api.get(`/api/v1/seller/orders/${id}`);
    return response.data;
  },

  updateOrderStatus: async (id: string, data: any) => {
    const response = await api.put(`/api/v1/seller/orders/${id}/status`, data);
    return response.data;
  },

  // Notifications
  getNotifications: async (params?: { skip?: number; limit?: number; unread_only?: boolean }) => {
    const response = await api.get('/api/v1/seller/notifications', { params });
    return response.data;
  },

  getUnreadCount: async () => {
    const response = await api.get('/api/v1/seller/notifications/unread-count');
    return response.data;
  },

  markNotificationRead: async (notificationId: string) => {
    const response = await api.put(`/api/v1/seller/notifications/${notificationId}/read`);
    return response.data;
  },

  markAllNotificationsRead: async () => {
    const response = await api.put('/api/v1/seller/notifications/mark-all-read');
    return response.data;
  },

  // Stock Management
  getStockInventory: async (params?: { low_stock_only?: boolean; search?: string }) => {
    const response = await api.get('/api/v1/seller/stock', { params });
    return response.data;
  },

  updateProductStock: async (productId: string, stockQuantity: number, notes?: string) => {
    const response = await api.put(`/api/v1/seller/stock/product/${productId}`, {
      stock_quantity: stockQuantity,
      notes
    });
    return response.data;
  },

  updateVariantStock: async (variantId: string, stockQuantity: number, notes?: string) => {
    const response = await api.put(`/api/v1/seller/stock/variant/${variantId}`, {
      stock_quantity: stockQuantity,
      notes
    });
    return response.data;
  },

  bulkUpdateStock: async (updates: Array<{ variant_id: string; stock_quantity: number; notes?: string }>) => {
    const response = await api.post('/api/v1/seller/stock/bulk-update', { updates });
    return response.data;
  },

  getLowStockCount: async () => {
    const response = await api.get('/api/v1/seller/stock/low-stock-count');
    return response.data;
  },
};

// Customer API
export const customerApi = {
  // Orders
  getOrders: async (params?: any) => {
    const response = await api.get('/api/v1/customer/orders', { params });
    return response.data;
  },

  getOrder: async (id: string) => {
    const response = await api.get(`/api/v1/customer/orders/${id}`);
    return response.data;
  },

  createOrder: async (data: any) => {
    const response = await api.post('/api/v1/customer/orders', data);
    return response.data;
  },

  requestReturn: async (id: string, data: { return_reason: string }) => {
    const response = await api.post(`/api/v1/customer/orders/${id}/return`, data);
    return response.data;
  },

  downloadInvoice: async (id: string) => {
    const response = await api.get(`/api/v1/customer/orders/${id}/invoice`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Products
  getProducts: async (params?: any) => {
    const response = await api.get('/api/v1/customer/products', { params });
    return response.data;
  },

  getProduct: async (id: string) => {
    const response = await api.get(`/api/v1/customer/products/${id}`);
    return response.data;
  },

  getProductsBySeller: async (sellerId: string, params?: any) => {
    const response = await api.get(`/api/v1/customer/products/seller/${sellerId}`, { params });
    return response.data;
  },
};

export default api; 