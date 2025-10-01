import React, { useState, useEffect } from 'react';
import { Users, ShoppingCart, Package, TrendingUp, UserCheck, AlertCircle } from 'lucide-react';
import { adminApi } from '../../lib/api';
import { Statistics, OrderStats } from '../../types/api';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  color: string;
  change?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon: Icon, color, change }) => (
  <div className="card p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-secondary-600">{title}</p>
        <p className="text-3xl font-bold text-secondary-900 mt-2">{value}</p>
        {change && (
          <p className="text-sm text-green-600 mt-1">
            <TrendingUp className="w-4 h-4 inline mr-1" />
            {change}
          </p>
        )}
      </div>
      <div className={`w-12 h-12 rounded-lg ${color} flex items-center justify-center`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
    </div>
  </div>
);

const Dashboard: React.FC = () => {
  const [userStats, setUserStats] = useState<Statistics | null>(null);
  const [orderStats, setOrderStats] = useState<OrderStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setIsLoading(true);
        const [userStatsData, orderStatsData] = await Promise.all([
          adminApi.getUserStats(),
          adminApi.getOrderStats(),
        ]);
        setUserStats(userStatsData);
        setOrderStats(orderStatsData);
      } catch (err: any) {
        setError('Failed to load dashboard data');
        console.error('Dashboard error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* User Statistics */}
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">User Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Users"
            value={userStats?.total_users || 0}
            icon={Users}
            color="bg-blue-500"
          />
          <StatCard
            title="Active Users"
            value={userStats?.active_users || 0}
            icon={UserCheck}
            color="bg-green-500"
          />
          <StatCard
            title="Total Sellers"
            value={userStats?.total_sellers || 0}
            icon={Package}
            color="bg-purple-500"
          />
          <StatCard
            title="Verified Sellers"
            value={userStats?.verified_sellers || 0}
            icon={UserCheck}
            color="bg-emerald-500"
          />
        </div>
      </div>

      {/* Order Statistics */}
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Order Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Orders"
            value={orderStats?.total_orders || 0}
            icon={ShoppingCart}
            color="bg-indigo-500"
          />
          <StatCard
            title="Pending Orders"
            value={orderStats?.pending_orders || 0}
            icon={AlertCircle}
            color="bg-yellow-500"
          />
          <StatCard
            title="Delivered Orders"
            value={orderStats?.delivered_orders || 0}
            icon={Package}
            color="bg-green-500"
          />
          <StatCard
            title="Total Revenue"
            value={`₹${(orderStats?.total_revenue || 0).toLocaleString()}`}
            icon={TrendingUp}
            color="bg-emerald-500"
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="card p-6 hover:shadow-md transition-shadow duration-200 cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Package className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <h4 className="font-semibold text-secondary-900">Product Approvals</h4>
                <p className="text-sm text-secondary-600">Review pending products</p>
              </div>
            </div>
          </div>

          <div className="card p-6 hover:shadow-md transition-shadow duration-200 cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <ShoppingCart className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h4 className="font-semibold text-secondary-900">Manage Orders</h4>
                <p className="text-sm text-secondary-600">Process customer orders</p>
              </div>
            </div>
          </div>

          <div className="card p-6 hover:shadow-md transition-shadow duration-200 cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h4 className="font-semibold text-secondary-900">User Management</h4>
                <p className="text-sm text-secondary-600">Manage users and sellers</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">System Status</h3>
        <div className="card p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between py-3 border-b border-secondary-100">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-secondary-700">API Server</span>
              </div>
              <span className="text-sm font-medium text-green-600">Online</span>
            </div>
            
            <div className="flex items-center justify-between py-3 border-b border-secondary-100">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-secondary-700">Database</span>
              </div>
              <span className="text-sm font-medium text-green-600">Connected</span>
            </div>
            
            <div className="flex items-center justify-between py-3">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span className="text-sm text-secondary-700">Pending Seller Verifications</span>
              </div>
              <span className="text-sm font-medium text-yellow-600">
                {userStats?.pending_seller_verification || 0}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 