import React from 'react';
import { UserCheck } from 'lucide-react';

const Sellers: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">Seller Management</h1>
        <p className="text-secondary-600">Manage seller accounts and verifications</p>
      </div>

      <div className="card p-12 text-center">
        <UserCheck className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-secondary-900 mb-2">Seller Management</h3>
        <p className="text-secondary-600">Seller management functionality will be implemented here.</p>
      </div>
    </div>
  );
};

export default Sellers; 