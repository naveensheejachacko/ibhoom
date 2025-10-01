import React from 'react';
import { Package } from 'lucide-react';

const Products: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">My Products</h1>
        <p className="text-secondary-600">Manage your product catalog</p>
      </div>

      <div className="card p-12 text-center">
        <Package className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-secondary-900 mb-2">Product Management</h3>
        <p className="text-secondary-600">Product management functionality will be implemented here.</p>
      </div>
    </div>
  );
};

export default Products; 