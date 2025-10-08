import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import AdminLayout from './components/Layout/AdminLayout';
import SellerLayout from './components/Layout/SellerLayout';
import Login from './components/Auth/Login';
import SellerRegistration from './components/Auth/SellerRegistration';
import AdminRegistration from './components/Auth/AdminRegistration';

// Admin Pages
import AdminDashboard from './pages/Admin/Dashboard';
import AdminProducts from './pages/Admin/Products';
import AdminCategories from './pages/Admin/Categories';
import AdminOrders from './pages/Admin/Orders';
import AdminUsers from './pages/Admin/Users';
import AdminSellers from './pages/Admin/Sellers';
import AdminCommissions from './pages/Admin/Commissions';

// Seller Pages
import SellerDashboard from './pages/Seller/Dashboard';
import SellerProducts from './pages/Seller/Products';
import SellerProductForm from './pages/Seller/ProductForm';
import ProfileSettings from './pages/Seller/ProfileSettings';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-secondary-50">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register/seller" element={<SellerRegistration />} />
            <Route path="/register/admin" element={<AdminRegistration />} />
            
            {/* Admin Routes */}
            <Route
              path="/admin/*"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminLayout>
                    <Routes>
                      <Route index element={<AdminDashboard />} />
                      <Route path="products" element={<AdminProducts />} />
                      <Route path="categories" element={<AdminCategories />} />
                      <Route path="orders" element={<AdminOrders />} />
                      <Route path="users" element={<AdminUsers />} />
                      <Route path="sellers" element={<AdminSellers />} />
                      <Route path="commissions" element={<AdminCommissions />} />
                    </Routes>
                  </AdminLayout>
                </ProtectedRoute>
              }
            />
            
            {/* Seller Routes */}
            <Route
              path="/seller/*"
              element={
                <ProtectedRoute allowedRoles={['seller']}>
                  <SellerLayout>
                    <Routes>
                      <Route index element={<SellerDashboard />} />
                      <Route path="products" element={<SellerProducts />} />
                      <Route path="products/new" element={<SellerProductForm />} />
                      <Route path="products/edit/:id" element={<SellerProductForm />} />
                      <Route path="profile" element={<ProfileSettings />} />
                    </Routes>
                  </SellerLayout>
                </ProtectedRoute>
              }
            />
            
            {/* Default Redirects */}
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
