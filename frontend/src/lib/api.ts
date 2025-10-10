import axios from 'axios';
import type { LoginRequest, LoginResponse } from '../types/auth';

const API_BASE_URL = 'http://localhost:8000';

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

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
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
  
  createCategory: async (data: any) => {
    const response = await api.post('/api/v1/admin/categories', data);
    return response.data;
  },
  
  updateCategory: async (id: string, data: any) => {
    const response = await api.put(`/api/v1/admin/categories/${id}`, data);
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
};

// Seller API
export const sellerApi = {
  // Products
  getProducts: async (params?: any) => {
    const response = await api.get('/api/v1/seller/products', { params });
    return response.data;
  },
  
  getProduct: async (id: string) => {
    const response = await api.get(`/api/v1/seller/products/${id}`);
    return response.data;
  },
  
  createProduct: async (data: any) => {
    const response = await api.post('/api/v1/seller/products', data);
    return response.data;
  },
  
  updateProduct: async (id: string, data: any) => {
    const response = await api.put(`/api/v1/seller/products/${id}`, data);
    return response.data;
  },
  
  deleteProduct: async (id: string) => {
    const response = await api.delete(`/api/v1/seller/products/${id}`);
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
};

export default api; 