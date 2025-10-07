import React from 'react';
import { ShoppingCart } from 'lucide-react';

const Orders: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">Order Management</h1>
        <p className="text-secondary-600">Process and manage customer orders</p>
      </div>

      <div className="card p-12 text-center">
        <ShoppingCart className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-secondary-900 mb-2">Orders Management</h3>
        <p className="text-secondary-600">Order management functionality will be implemented here.</p>
      </div>
    </div>
  );
};

export default Orders; 