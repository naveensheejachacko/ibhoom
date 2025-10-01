import React from 'react';
import { Plus } from 'lucide-react';

const ProductForm: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">Add Product</h1>
        <p className="text-secondary-600">Create a new product for approval</p>
      </div>

      <div className="card p-12 text-center">
        <Plus className="w-12 h-12 text-secondary-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-secondary-900 mb-2">Product Form</h3>
        <p className="text-secondary-600">Product creation form will be implemented here.</p>
      </div>
    </div>
  );
};

export default ProductForm; 