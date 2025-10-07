import React from 'react';
import { Percent } from 'lucide-react';

const Commissions: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">Commission Management</h1>
        <p className="text-secondary-600">Manage commission rates and settings</p>
      </div>

      <div className="card p-12 text-center">
        <Percent className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-secondary-900 mb-2">Commission Management</h3>
        <p className="text-secondary-600">Commission management functionality will be implemented here.</p>
      </div>
    </div>
  );
};

export default Commissions; 