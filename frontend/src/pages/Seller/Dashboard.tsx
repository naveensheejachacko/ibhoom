import React, { useState, useEffect } from 'react';
import { Package, Clock, CheckCircle, XCircle, Plus, TrendingUp, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';
import { sellerApi } from '../../lib/api';
import { Product } from '../../types/api';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  color: string;
  description: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon: Icon, color, description }) => (
  <div className="card p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-secondary-600">{title}</p>
        <p className="text-3xl font-bold text-secondary-900 mt-2">{value}</p>
        <p className="text-sm text-secondary-500 mt-1">{description}</p>
      </div>
      <div className={`w-12 h-12 rounded-lg ${color} flex items-center justify-center`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
    </div>
  </div>
);

interface RecentProductProps {
  product: Product;
}

const RecentProductCard: React.FC<RecentProductProps> = ({ product }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="flex items-center justify-between p-4 border border-secondary-200 rounded-lg">
      <div className="flex-1">
        <h4 className="font-medium text-secondary-900">{product.name}</h4>
        <p className="text-sm text-secondary-600">₹{product.seller_price?.toLocaleString()}</p>
      </div>
      <div className="flex items-center space-x-3">
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(product.status)}`}>
          {product.status}
        </span>
        <button className="text-primary-600 hover:text-primary-700">
          <Eye className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

const Dashboard: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [approvedCount, setApprovedCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      const [productsData, pendingData, approvedData] = await Promise.all([
        sellerApi.getProducts({ limit: 5 }), // Get recent 5 products
        sellerApi.getPendingCount(),
        sellerApi.getApprovedCount(),
      ]);
      
      setProducts(productsData.items || productsData);
      setPendingCount(pendingData.count || 0);
      setApprovedCount(approvedData.count || 0);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const totalProducts = products.length;
  const draftProducts = products.filter(p => p.status === 'draft').length;
  const rejectedProducts = products.filter(p => p.status === 'rejected').length;

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="card p-6 bg-gradient-to-r from-primary-50 to-primary-100 border-primary-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-primary-900 mb-2">Welcome to Your Store!</h2>
            <p className="text-primary-700">
              Manage your products, track sales, and grow your business with our platform.
            </p>
          </div>
          <Link
            to="/seller/products/new"
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Add Product</span>
          </Link>
        </div>
      </div>

      {/* Statistics */}
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Product Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Products"
            value={totalProducts}
            icon={Package}
            color="bg-blue-500"
            description="All your products"
          />
          <StatCard
            title="Pending Approval"
            value={pendingCount}
            icon={Clock}
            color="bg-yellow-500"
            description="Awaiting admin review"
          />
          <StatCard
            title="Approved Products"
            value={approvedCount}
            icon={CheckCircle}
            color="bg-green-500"
            description="Live on marketplace"
          />
          <StatCard
            title="Rejected Products"
            value={rejectedProducts}
            icon={XCircle}
            color="bg-red-500"
            description="Need revision"
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            to="/seller/products/new"
            className="card p-6 hover:shadow-md transition-shadow duration-200 group"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-colors">
                <Plus className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h4 className="font-semibold text-secondary-900">Add New Product</h4>
                <p className="text-sm text-secondary-600">Upload a new product for approval</p>
              </div>
            </div>
          </Link>

          <Link
            to="/seller/products?status=pending"
            className="card p-6 hover:shadow-md transition-shadow duration-200 group"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center group-hover:bg-yellow-200 transition-colors">
                <Clock className="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <h4 className="font-semibold text-secondary-900">Pending Products</h4>
                <p className="text-sm text-secondary-600">View products awaiting approval</p>
              </div>
            </div>
          </Link>

          <Link
            to="/seller/products"
            className="card p-6 hover:shadow-md transition-shadow duration-200 group"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
                <Package className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h4 className="font-semibold text-secondary-900">All Products</h4>
                <p className="text-sm text-secondary-600">Manage your product catalog</p>
              </div>
            </div>
          </Link>
        </div>
      </div>

      {/* Recent Products */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-secondary-900">Recent Products</h3>
          <Link
            to="/seller/products"
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            View All
          </Link>
        </div>
        
        {products.length === 0 ? (
          <div className="card p-12 text-center">
            <Package className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-secondary-900 mb-2">No Products Yet</h4>
            <p className="text-secondary-600 mb-4">Start by adding your first product to the marketplace.</p>
            <Link to="/seller/products/new" className="btn-primary">
              Add Your First Product
            </Link>
          </div>
        ) : (
          <div className="card p-6">
            <div className="space-y-4">
              {products.map((product) => (
                <RecentProductCard key={product.id} product={product} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Tips Section */}
      <div className="card p-6 bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
        <div className="flex items-start space-x-4">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <TrendingUp className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <h4 className="font-semibold text-green-900 mb-2">Tips for Success</h4>
            <ul className="text-sm text-green-800 space-y-1">
              <li>• Upload high-quality product images to increase approval chances</li>
              <li>• Write detailed product descriptions with all specifications</li>
              <li>• Set competitive prices to attract more customers</li>
              <li>• Ensure accurate stock quantities to avoid order issues</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 